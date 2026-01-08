"""
Admin Routes - For platform administrators
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User, QRCode, QRScan, UserRole, SubscriptionPlan
from app.utils.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# Schemas
class UserAdmin(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    subscription_plan: str
    role: str
    is_verified: bool
    created_at: datetime
    total_qr_codes: int = 0
    total_scans: int = 0
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    subscription_plan: Optional[SubscriptionPlan] = None
    role: Optional[UserRole] = None
    is_verified: Optional[bool] = None


class PlatformStats(BaseModel):
    total_users: int
    free_users: int
    pro_users: int
    business_users: int
    total_qr_codes: int
    total_scans: int
    active_qr_codes: int


class ConfigUpdate(BaseModel):
    free_qr_limit: Optional[int] = None
    pro_price: Optional[float] = None
    business_price: Optional[float] = None
    site_name: Optional[str] = None
    primary_color: Optional[str] = None


# Middleware to check admin role
def get_current_admin(current_user: User = Depends(get_current_user)):
    """Verify user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get platform statistics"""
    
    total_users = db.query(User).count()
    free_users = db.query(User).filter(User.subscription_plan == SubscriptionPlan.FREE).count()
    pro_users = db.query(User).filter(User.subscription_plan == SubscriptionPlan.PRO).count()
    business_users = db.query(User).filter(User.subscription_plan == SubscriptionPlan.BUSINESS).count()
    
    total_qr_codes = db.query(QRCode).count()
    active_qr_codes = db.query(QRCode).filter(QRCode.is_active == True).count()
    total_scans = db.query(func.sum(QRCode.total_scans)).scalar() or 0
    
    return PlatformStats(
        total_users=total_users,
        free_users=free_users,
        pro_users=pro_users,
        business_users=business_users,
        total_qr_codes=total_qr_codes,
        total_scans=total_scans,
        active_qr_codes=active_qr_codes
    )


@router.get("/users", response_model=List[UserAdmin])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all users with stats"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        qr_count = db.query(QRCode).filter(QRCode.user_id == user.id).count()
        total_scans = db.query(func.sum(QRCode.total_scans)).filter(QRCode.user_id == user.id).scalar() or 0
        
        result.append(UserAdmin(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            subscription_plan=user.subscription_plan.value,
            role=user.role.value,
            is_verified=user.is_verified,
            created_at=user.created_at,
            total_qr_codes=qr_count,
            total_scans=total_scans
        ))
    
    return result


@router.put("/users/{user_id}", response_model=UserAdmin)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Update user details (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.subscription_plan:
        user.subscription_plan = user_update.subscription_plan
    if user_update.role:
        user.role = user_update.role
    if user_update.is_verified is not None:
        user.is_verified = user_update.is_verified
    
    db.commit()
    db.refresh(user)
    
    # Get stats
    qr_count = db.query(QRCode).filter(QRCode.user_id == user.id).count()
    total_scans = db.query(func.sum(QRCode.total_scans)).filter(QRCode.user_id == user.id).scalar() or 0
    
    return UserAdmin(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        subscription_plan=user.subscription_plan.value,
        role=user.role.value,
        is_verified=user.is_verified,
        created_at=user.created_at,
        total_qr_codes=qr_count,
        total_scans=total_scans
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete user and all their data"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting other admins
    if user.role == UserRole.ADMIN and user.id != admin.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete other administrators"
        )
    
    # Delete user's QR codes first
    db.query(QRCode).filter(QRCode.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
