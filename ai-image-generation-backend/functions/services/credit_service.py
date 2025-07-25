"""
Credit Service - Handles all credit-related operations
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from firebase_admin import firestore
from models.transaction import CreditTransaction, TransactionType

logger = logging.getLogger(__name__)


class CreditService:
    """Service for managing user credits and transactions"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.users_collection = db.collection("users")
        self.transactions_collection = db.collection("credit_transactions")
    
    def get_user_credits(self, user_id: str) -> int:
        """
        Get current credit balance for a user
        
        Args:
            user_id: The user's ID
            
        Returns:
            Current credit balance (0 if user doesn't exist)
        """
        try:
            user_doc = self.users_collection.document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict().get("credits", 0)
            return 0
        except Exception as e:
            logger.error(f"Error getting user credits: {str(e)}")
            return 0
    
    def deduct_credits(
        self,
        transaction: firestore.Transaction,
        user_id: str,
        amount: int,
        generation_request_id: str
    ) -> bool:
        """
        Deduct credits from user account atomically
        
        Args:
            transaction: Firestore transaction object
            user_id: The user's ID
            amount: Amount of credits to deduct
            generation_request_id: ID of the generation request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user document reference
            user_ref = self.users_collection.document(user_id)
            user_doc = transaction.get(user_ref)
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return False
            
            current_credits = user_doc.to_dict().get("credits", 0)
            
            if current_credits < amount:
                logger.error(f"Insufficient credits for user {user_id}")
                return False
            
            # Update user credits
            new_credits = current_credits - amount
            transaction.update(user_ref, {
                "credits": new_credits,
                "updatedAt": datetime.now(timezone.utc)
            })
            
            # Create transaction record
            credit_transaction = CreditTransaction(
                user_id=user_id,
                type=TransactionType.DEDUCTION,
                credits=amount,
                generation_request_id=generation_request_id,
                reason=f"Image generation - {amount} credits"
            )
            
            transaction_ref = self.transactions_collection.document()
            credit_transaction.transaction_id = transaction_ref.id
            transaction.set(transaction_ref, credit_transaction.to_dict())
            
            logger.info(f"Deducted {amount} credits from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deducting credits: {str(e)}")
            return False
    
    def refund_credits(
        self,
        user_id: str,
        amount: int,
        generation_request_id: str
    ) -> bool:
        """
        Refund credits to user account
        
        Args:
            user_id: The user's ID
            amount: Amount of credits to refund
            generation_request_id: ID of the failed generation request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use a transaction for atomic update
            @firestore.transactional
            def refund_transaction(transaction):
                # Get user document
                user_ref = self.users_collection.document(user_id)
                user_doc = transaction.get(user_ref)
                
                if not user_doc.exists:
                    # Create user if doesn't exist (edge case)
                    transaction.set(user_ref, {
                        "userId": user_id,
                        "credits": amount,
                        "createdAt": datetime.now(timezone.utc),
                        "updatedAt": datetime.now(timezone.utc)
                    })
                else:
                    # Update existing user credits
                    current_credits = user_doc.to_dict().get("credits", 0)
                    new_credits = current_credits + amount
                    transaction.update(user_ref, {
                        "credits": new_credits,
                        "updatedAt": datetime.now(timezone.utc)
                    })
                
                # Create refund transaction record
                credit_transaction = CreditTransaction(
                    user_id=user_id,
                    type=TransactionType.REFUND,
                    credits=amount,
                    generation_request_id=generation_request_id,
                    reason=f"Refund for failed generation - {amount} credits"
                )
                
                transaction_ref = self.transactions_collection.document()
                credit_transaction.transaction_id = transaction_ref.id
                transaction.set(transaction_ref, credit_transaction.to_dict())
                
                return True
            
            # Execute transaction
            transaction = self.db.transaction()
            refund_transaction(transaction)
            
            logger.info(f"Refunded {amount} credits to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error refunding credits: {str(e)}")
            return False
    
    def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get credit transaction history for a user
        
        Args:
            user_id: The user's ID
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        try:
            # Query transactions for user, ordered by timestamp descending
            query = (
                self.transactions_collection
                .where("userId", "==", user_id)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            
            transactions = []
            for doc in query.stream():
                transaction_data = doc.to_dict()
                transaction_data["transactionId"] = doc.id
                transactions.append(transaction_data)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return []
    
    def create_user_with_credits(
        self,
        user_id: str,
        initial_credits: int = 50,
        email: Optional[str] = None
    ) -> bool:
        """
        Create a new user with initial credits
        
        Args:
            user_id: The user's ID
            initial_credits: Initial credit balance
            email: User's email (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user_data = {
                "userId": user_id,
                "credits": initial_credits,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            if email:
                user_data["email"] = email
            
            self.users_collection.document(user_id).set(user_data)
            
            # Create initial credit transaction
            credit_transaction = CreditTransaction(
                user_id=user_id,
                type=TransactionType.CREDIT,
                credits=initial_credits,
                reason=f"Initial credit allocation - {initial_credits} credits"
            )
            
            transaction_ref = self.transactions_collection.document()
            credit_transaction.transaction_id = transaction_ref.id
            self.transactions_collection.document(transaction_ref.id).set(
                credit_transaction.to_dict()
            )
            
            logger.info(f"Created user {user_id} with {initial_credits} credits")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False