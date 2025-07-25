"""
models/transaction.py - Credit Transaction model
"""

from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type enum"""
    DEDUCTION = "deduction"
    REFUND = "refund"
    CREDIT = "credit"  # For initial credits or manual additions


class CreditTransaction:
    """Credit transaction model"""
    
    def __init__(
        self,
        user_id: str,
        type: TransactionType,
        credits: int,
        reason: str,
        transaction_id: Optional[str] = None,
        generation_request_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.type = type
        self.credits = credits
        self.reason = reason
        self.generation_request_id = generation_request_id
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        data = {
            "userId": self.user_id,
            "type": self.type,
            "credits": self.credits,
            "reason": self.reason,
            "timestamp": self.timestamp
        }
        
        if self.transaction_id:
            data["transactionId"] = self.transaction_id
        if self.generation_request_id:
            data["generationRequestId"] = self.generation_request_id
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create CreditTransaction instance from dictionary"""
        return cls(
            transaction_id=data.get("transactionId"),
            user_id=data.get("userId"),
            type=data.get("type"),
            credits=data.get("credits", 0),
            reason=data.get("reason", ""),
            generation_request_id=data.get("generationRequestId"),
            timestamp=data.get("timestamp")
        )