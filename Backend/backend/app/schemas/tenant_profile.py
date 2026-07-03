from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class TenantProfileCreateRequest(BaseModel):
    preferred_location: str = Field(..., max_length=190)
    budget_min: float = Field(..., ge=0)
    budget_max: float = Field(..., ge=0)
    move_in_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_budget_range(self):
        if self.budget_max < self.budget_min:
            raise ValueError("budget_max must be greater than or equal to budget_min")
        return self


class TenantProfileUpdateRequest(BaseModel):
    preferred_location: Optional[str] = Field(None, max_length=190)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    move_in_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class TenantProfileResponse(BaseModel):
    id: int
    user_id: int
    preferred_location: str
    budget_min: float
    budget_max: float
    move_in_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
