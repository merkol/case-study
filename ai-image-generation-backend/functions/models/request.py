"""
models/request.py - Generation Request model
"""

from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class RequestStatus(str, Enum):
    """Generation request status enum"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationRequest:
    """Generation request model"""
    
    def __init__(
        self,
        user_id: str,
        model: str,
        style: str,
        color: str,
        size: str,
        prompt: str,
        credits_charged: int,
        request_id: Optional[str] = None,
        status: RequestStatus = RequestStatus.PENDING,
        image_url: Optional[str] = None,
        error: Optional[str] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.model = model
        self.style = style
        self.color = color
        self.size = size
        self.prompt = prompt
        self.status = status
        self.image_url = image_url
        self.error = error
        self.credits_charged = credits_charged
        self.created_at = created_at or datetime.now(timezone.utc)
        self.completed_at = completed_at
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        data = {
            "userId": self.user_id,
            "model": self.model,
            "style": self.style,
            "color": self.color,
            "size": self.size,
            "prompt": self.prompt,
            "status": self.status,
            "creditsCharged": self.credits_charged,
            "createdAt": self.created_at
        }
        
        if self.request_id:
            data["requestId"] = self.request_id
        if self.image_url:
            data["imageUrl"] = self.image_url
        if self.error:
            data["error"] = self.error
        if self.completed_at:
            data["completedAt"] = self.completed_at
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create GenerationRequest instance from dictionary"""
        return cls(
            request_id=data.get("requestId"),
            user_id=data.get("userId"),
            model=data.get("model"),
            style=data.get("style"),
            color=data.get("color"),
            size=data.get("size"),
            prompt=data.get("prompt"),
            status=data.get("status", RequestStatus.PENDING),
            image_url=data.get("imageUrl"),
            error=data.get("error"),
            credits_charged=data.get("creditsCharged", 0),
            created_at=data.get("createdAt"),
            completed_at=data.get("completedAt")
        )
