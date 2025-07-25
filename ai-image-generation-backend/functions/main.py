"""
Main entry point for Firebase Cloud Functions
"""

import json
import logging
from datetime import datetime, timezone
from firebase_functions import https_fn, scheduler_fn, options
from firebase_admin import initialize_app, firestore
from services.credit_service import CreditService
from services.generation_service import GenerationService
from services.report_service import ReportService
from validators.request_validator import RequestValidator
from models.request import GenerationRequest
from models.transaction import TransactionType

# Initialize Firebase Admin
initialize_app()

# Initialize services
db = firestore.client()
credit_service = CreditService(db)
generation_service = GenerationService(db)
report_service = ReportService(db)
validator = RequestValidator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["POST"],
    )
)
def createGenerationRequest(req: https_fn.Request) -> https_fn.Response:
    """
    Create a new image generation request

    Expected payload:
    {
        "userId": str,
        "model": str,
        "style": str,
        "color": str,
        "size": str,
        "prompt": str
    }
    """
    try:
        # Parse request body
        if req.method != "POST":
            return https_fn.Response(
                json.dumps({"error": "Method not allowed"}),
                status=405,
                headers={"Content-Type": "application/json"},
            )

        data = req.get_json()
        if not data:
            return https_fn.Response(
                json.dumps({"error": "Invalid request body"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Validate request
        validation_result = validator.validate_generation_request(data)
        if not validation_result["valid"]:
            return https_fn.Response(
                json.dumps({"error": validation_result["error"]}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Extract validated data
        user_id = data["userId"]
        model = data["model"]
        style = data["style"]
        color = data["color"]
        size = data["size"]
        prompt = data["prompt"]

        # Calculate credit cost
        credit_cost = validator.get_credit_cost(size)

        # Check user credits
        user_credits = credit_service.get_user_credits(user_id)
        if user_credits < credit_cost:
            return https_fn.Response(
                json.dumps(
                    {
                        "error": "Insufficient credits",
                        "required": credit_cost,
                        "available": user_credits,
                    }
                ),
                status=402,
                headers={"Content-Type": "application/json"},
            )

        # Create generation request
        generation_request = GenerationRequest(
            user_id=user_id,
            model=model,
            style=style,
            color=color,
            size=size,
            prompt=prompt,
            credits_charged=credit_cost,
        )

        # Save request to database
        request_ref = db.collection("generation_requests").document()
        generation_request.request_id = request_ref.id

        # Start transaction for atomic credit deduction
        @firestore.transactional
        def create_request_transaction(transaction):
            # Deduct credits
            success = credit_service.deduct_credits(
                transaction, user_id, credit_cost, request_ref.id
            )
            if not success:
                raise Exception("Failed to deduct credits")

            # Save generation request
            transaction.set(request_ref, generation_request.to_dict())

            return True

        # Execute transaction
        transaction = db.transaction()
        create_request_transaction(transaction)

        # Simulate AI generation
        try:
            image_url = generation_service.generate_image(
                generation_request.request_id, model, style, color, size, prompt
            )

            # Update request with success
            request_ref.update(
                {
                    "status": "completed",
                    "imageUrl": image_url,
                    "completedAt": datetime.now(timezone.utc),
                }
            )

            # Return success response
            return https_fn.Response(
                json.dumps(
                    {
                        "generationRequestId": generation_request.request_id,
                        "deductedCredits": credit_cost,
                        "imageUrl": image_url,
                    }
                ),
                status=200,
                headers={"Content-Type": "application/json"},
            )

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")

            # Update request with failure
            request_ref.update(
                {
                    "status": "failed",
                    "error": str(e),
                    "completedAt": datetime.now(timezone.utc),
                }
            )

            # Refund credits
            credit_service.refund_credits(
                user_id, credit_cost, generation_request.request_id
            )

            return https_fn.Response(
                json.dumps(
                    {
                        "error": "Image generation failed",
                        "details": str(e),
                        "creditsRefunded": credit_cost,
                    }
                ),
                status=500,
                headers={"Content-Type": "application/json"},
            )

    except Exception as e:
        logger.error(f"Error in createGenerationRequest: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )


@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["GET"],
    )
)
def getUserCredits(req: https_fn.Request) -> https_fn.Response:
    """
    Get user's current credit balance and transaction history

    Query parameters:
    - userId: str (required)
    """
    try:
        # Validate method
        if req.method != "GET":
            return https_fn.Response(
                json.dumps({"error": "Method not allowed"}),
                status=405,
                headers={"Content-Type": "application/json"},
            )

        # Get userId from query parameters
        user_id = req.args.get("userId")
        if not user_id:
            return https_fn.Response(
                json.dumps({"error": "userId parameter is required"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Get current credits
        current_credits = credit_service.get_user_credits(user_id)

        # Get transaction history
        transactions = credit_service.get_transaction_history(user_id)

        # Format response
        response = {
            "currentCredits": current_credits,
            "transactions": [
                {
                    "id": t["transactionId"],
                    "type": t["type"],
                    "credits": t["credits"],
                    "generationRequestId": t.get("generationRequestId", ""),
                    "timestamp": t["timestamp"].isoformat()
                    if hasattr(t["timestamp"], "isoformat")
                    else str(t["timestamp"]),
                }
                for t in transactions
            ],
        }

        return https_fn.Response(
            json.dumps(response),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        logger.error(f"Error in getUserCredits: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )


@scheduler_fn.on_schedule(
    schedule="0 0 * * 1",  # Every Monday at 00:00 UTC
    timezone=scheduler_fn.Timezone("UTC"),
    memory=options.MemoryOption.MB_512,
)
def scheduleWeeklyReport(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Generate weekly usage report
    Runs every Monday at 00:00 UTC
    """
    try:
        logger.info("Starting weekly report generation")

        # Generate report
        report_id = report_service.generate_weekly_report()

        logger.info(f"Weekly report generated successfully: {report_id}")

        # Return success (for monitoring)
        return {"reportStatus": "success", "reportId": report_id}

    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        raise e
