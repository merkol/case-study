"""
models/user.py - User model
"""

from datetime import datetime, timezone
from typing import Optional


class User:
    """User model for the system"""
    
    def __init__(
        self,
        user_id: str,
        credits: int = 0,
        email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.credits = credits
        self.email = email
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        data = {
            "userId": self.user_id,
            "credits": self.credits,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
        if self.email:
            data["email"] = self.email
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create User instance from dictionary"""
        return cls(
            user_id=data.get("userId"),
            credits=data.get("credits", 0),
            email=data.get("email"),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt")
        )
