from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_tenant
from app.models.user import User
from app.models.tenant_profile import TenantProfile
from app.schemas.tenant_profile import (
    TenantProfileCreateRequest,
    TenantProfileUpdateRequest,
    TenantProfileResponse,
)

router = APIRouter(prefix="/api/tenant", tags=["Tenant Profile"])


@router.post("/profile", response_model=TenantProfileResponse, status_code=201)
def create_profile(
    payload: TenantProfileCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_tenant)
):
    existing = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists, use PUT to update")

    profile = TenantProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile", response_model=TenantProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(require_tenant)):
    profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant profile not found")
    return profile


@router.put("/profile", response_model=TenantProfileResponse)
def update_profile(
    payload: TenantProfileUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_tenant)
):
    profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant profile not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
