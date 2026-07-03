from datetime import datetime
from pydantic import BaseModel, Field


class CompatibilityResponse(BaseModel):
    id: int
    tenant_id: int
    listing_id: int
    score: float = Field(..., ge=0, le=100)
    explanation: str
    source: str  # "llm" | "fallback"
    computed_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LLMCompatibilityResult(BaseModel):
    """Shape the LLM is instructed to return as JSON."""
    score: float = Field(..., ge=0, le=100)
    explanation: str
