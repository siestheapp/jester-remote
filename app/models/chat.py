"""
Chat-related data models for the application.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatContext(BaseModel):
    """Context for chat interactions."""
    size_guide_id: Optional[str] = Field(None, description="Related size guide ID")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional context metadata")
    relevant_chunks: List[str] = Field(default_factory=list, description="Relevant knowledge base chunks")

class ChatSession(BaseModel):
    """Complete chat session."""
    id: Optional[str] = Field(None, description="Session identifier")
    messages: List[ChatMessage] = Field(default_factory=list)
    context: ChatContext = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "How should I measure chest width?",
                        "timestamp": "2025-04-23T22:36:26Z"
                    }
                ],
                "context": {
                    "size_guide_id": "guide123",
                    "metadata": {
                        "brand": "Example Brand",
                        "category": "Shirts"
                    }
                }
            }
        } 