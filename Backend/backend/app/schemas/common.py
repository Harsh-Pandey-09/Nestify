from typing import Optional
from pydantic import BaseModel


class MessageResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class AdminActivitySummary(BaseModel):
    total_users: int
    total_tenants: int
    total_owners: int
    total_listings: int
    active_listings: int
    filled_listings: int
    total_interests: int
    pending_interests: int
    accepted_interests: int
    total_messages: int
    total_compatibility_scores: int
    llm_scores: int
    fallback_scores: int
