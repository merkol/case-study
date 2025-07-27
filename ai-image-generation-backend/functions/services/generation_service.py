"""
Generation Service - Simulates AI image generation with configurable failure rates
"""

import logging
import random
import time
from typing import Optional
from firebase_admin import firestore

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for simulating AI image generation"""

    # Configurable failure rates
    MODEL_A_FAILURE_RATE = 0.05  # 5% failure rate
    MODEL_B_FAILURE_RATE = 0.05  # 5% failure rate

    # Placeholder image URLs for each model
    MODEL_A_BASE_URL = "https://placeholder-model-a.com/image"
    MODEL_B_BASE_URL = "https://placeholder-model-b.com/image"

    def __init__(self, db: firestore.Client):
        self.db = db
        self.requests_collection = db.collection("generation_requests")

    def generate_image(
        self,
        request_id: str,
        model: str,
        style: str,
        color: str,
        size: str,
        prompt: str,
    ) -> str:
        """
        Simulate AI image generation with configurable failure

        Args:
            request_id: Generation request ID
            model: AI model to use (Model A or Model B)
            style: Image style
            color: Color scheme
            size: Image dimensions
            prompt: Generation prompt

        Returns:
            Generated image URL

        Raises:
            Exception: If generation fails
        """
        try:
            # Simulate processing time (0.5 to 2 seconds)
            processing_time = random.uniform(0.5, 2.0)
            time.sleep(processing_time)

            # Determine failure rate based on model
            failure_rate = (
                self.MODEL_A_FAILURE_RATE
                if model == "Model A"
                else self.MODEL_B_FAILURE_RATE
            )

            # Simulate random failure
            if random.random() < failure_rate:
                error_messages = [
                    "AI model temporarily unavailable",
                    "Generation timeout",
                    "Invalid prompt processing",
                    "Resource allocation failed",
                    "Model inference error",
                ]
                error_msg = random.choice(error_messages)
                logger.error(f"Simulated generation failure: {error_msg}")
                raise Exception(error_msg)

            # Generate unique image URL based on model
            timestamp = int(time.time() * 1000)
            unique_id = f"{request_id}_{timestamp}"

            if model == "Model A":
                image_url = f"{self.MODEL_A_BASE_URL}_{unique_id}.jpg"
            else:  # Model B
                image_url = f"{self.MODEL_B_BASE_URL}_{unique_id}.jpg"

            # Log successful generation
            logger.info(
                f"Successfully generated image for request {request_id} "
                f"using {model} with style={style}, color={color}, size={size}"
            )

            return image_url

        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            raise
