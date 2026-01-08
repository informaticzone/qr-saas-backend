"""
Analytics Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, QRCode, QRScan
from app.utils.auth import get_current_user
import user_agents

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Schemas
class ScanEvent(BaseModel):
    timestamp: str
    country: str | None
    city: str | None
    device_type: str | None
    os: str | None


class QRAnalytics(BaseModel):
    qr_code_id: int
    total_scans: int
    scans_today: int
    scans_this_week: int
    scans_this_month: int
    top_countries: List[Dict[str, int]]
    top_devices: List[Dict[str, int]]
    recent_scans: List[ScanEvent]


@router.get("/{qr_id}", response_model=QRAnalytics)
async def get_qr_analytics(
    qr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for specific QR code"""
    
    # Verify ownership
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Check if user has premium (analytics requires premium)
    if not current_user.is_premium:
        raise HTTPException(
            status_code=403,
            detail="Analytics require PRO subscription"
        )
    
    # Get time ranges
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total scans
    total_scans = db.query(QRScan).filter(QRScan.qr_code_id == qr_id).count()
    
    # Scans today
    scans_today = db.query(QRScan).filter(
        QRScan.qr_code_id == qr_id,
        QRScan.scanned_at >= today
    ).count()
    
    # Scans this week
    scans_week = db.query(QRScan).filter(
        QRScan.qr_code_id == qr_id,
        QRScan.scanned_at >= week_ago
    ).count()
    
    # Scans this month
    scans_month = db.query(QRScan).filter(
        QRScan.qr_code_id == qr_id,
        QRScan.scanned_at >= month_ago
    ).count()
    
    # Top countries
    top_countries = db.query(
        QRScan.country,
        func.count(QRScan.id).label('count')
    ).filter(
        QRScan.qr_code_id == qr_id,
        QRScan.country.isnot(None)
    ).group_by(QRScan.country).order_by(func.count(QRScan.id).desc()).limit(5).all()
    
    # Top devices
    top_devices = db.query(
        QRScan.device_type,
        func.count(QRScan.id).label('count')
    ).filter(
        QRScan.qr_code_id == qr_id,
        QRScan.device_type.isnot(None)
    ).group_by(QRScan.device_type).order_by(func.count(QRScan.id).desc()).limit(5).all()
    
    # Recent scans (last 10)
    recent_scans = db.query(QRScan).filter(
        QRScan.qr_code_id == qr_id
    ).order_by(QRScan.scanned_at.desc()).limit(10).all()
    
    return {
        "qr_code_id": qr_id,
        "total_scans": total_scans,
        "scans_today": scans_today,
        "scans_this_week": scans_week,
        "scans_this_month": scans_month,
        "top_countries": [{"country": c[0], "count": c[1]} for c in top_countries],
        "top_devices": [{"device": d[0], "count": d[1]} for d in top_devices],
        "recent_scans": [
            {
                "timestamp": scan.scanned_at.isoformat(),
                "country": scan.country,
                "city": scan.city,
                "device_type": scan.device_type,
                "os": scan.os
            }
            for scan in recent_scans
        ]
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary analytics for user dashboard"""
    
    # Get all user's QR codes
    qr_codes = db.query(QRCode).filter(QRCode.user_id == current_user.id).all()
    qr_ids = [qr.id for qr in qr_codes]
    
    # Total QR codes
    total_qr_codes = len(qr_codes)
    
    # Total scans across all QR codes
    total_scans = db.query(QRScan).filter(QRScan.qr_code_id.in_(qr_ids)).count() if qr_ids else 0
    
    # Scans this month
    month_ago = datetime.utcnow() - timedelta(days=30)
    scans_this_month = db.query(QRScan).filter(
        QRScan.qr_code_id.in_(qr_ids),
        QRScan.scanned_at >= month_ago
    ).count() if qr_ids else 0
    
    # Most scanned QR
    most_scanned = None
    if qr_ids:
        top_qr = db.query(
            QRCode.id,
            QRCode.title,
            func.count(QRScan.id).label('scan_count')
        ).join(QRScan).filter(
            QRCode.id.in_(qr_ids)
        ).group_by(QRCode.id, QRCode.title).order_by(func.count(QRScan.id).desc()).first()
        
        if top_qr:
            most_scanned = {
                "id": top_qr[0],
                "title": top_qr[1],
                "scans": top_qr[2]
            }
    
    return {
        "total_qr_codes": total_qr_codes,
        "total_scans": total_scans,
        "scans_this_month": scans_this_month,
        "scan_limit": current_user.scan_limit,
        "most_scanned_qr": most_scanned,
        "subscription_plan": current_user.subscription_plan.value
    }
