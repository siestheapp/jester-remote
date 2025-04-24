"""
API schemas for chat operations.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.models.chat import ChatMessage, ChatContext, ChatSession

class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message."""
    message: str = Field(..., description="User message content")
    size_guide_id: Optional[str] = Field(None, description="Related size guide ID")
    context_metadata: Dict[str, str] = Field(default_factory=dict, description="Additional context")

class ChatMessageResponse(BaseModel):
    """Response schema for chat messages."""
    message: ChatMessage
    context: ChatContext
    session_id: str = Field(..., description="Chat session identifier")

class ChatHistoryRequest(BaseModel):
    """Request schema for retrieving chat history."""
    session_id: str = Field(..., description="Chat session identifier")
    limit: int = Field(default=50, description="Maximum number of messages to return")
    before_timestamp: Optional[str] = Field(None, description="Get messages before this timestamp")

class ChatHistoryResponse(BaseModel):
    """Response schema for chat history."""
    session: ChatSession
    has_more: bool = Field(default=False, description="Whether more messages exist") 