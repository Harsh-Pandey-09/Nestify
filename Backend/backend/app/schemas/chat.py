from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessageCreateRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    id: int
    interest_id: int
    sender_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    interest_id: int
    messages: List[ChatMessageResponse]


class WSIncomingMessage(BaseModel):
    """Message sent by client over the WebSocket."""
    type: str = "message"  # "message" | "typing" | "read"
    message: Optional[str] = None


class WSOutgoingMessage(BaseModel):
    """Message broadcast by server over the WebSocket."""
    type: str  # "message" | "typing" | "read" | "error" | "connected"
    data: Optional[dict] = None
