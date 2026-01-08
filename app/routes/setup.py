"""
Setup routes for initial platform configuration
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.config import settings

router = APIRouter(tags=["setup"])


@router.get("/setup/init-admin")
async def initialize_first_admin(
    email: str,
    secret_key: str,
    db: Session = Depends(get_db)
):
    """
    Initialize the first admin user
    This endpoint can only be used once and requires a secret key
    
    Usage:
    GET /api/setup/init-admin?email=tuaemail@example.com&secret_key=ADMIN_SETUP_KEY
    """
    # Check secret key
    if secret_key != settings.ADMIN_SETUP_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    # Check if an admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail=f"Admin already exists: {existing_admin.email}"
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email '{email}' not found")
    
    # Promote to admin
    user.role = UserRole.ADMIN
    user.is_verified = True
    db.commit()
    
    return {
        "success": True,
        "message": f"User '{email}' promoted to admin",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/setup/check-admin")
async def check_admin_exists(db: Session = Depends(get_db)):
    """
    Check if an admin user exists in the system
    """
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    return {
        "admin_exists": admin is not None,
        "admin_email": admin.email if admin else None
    }
