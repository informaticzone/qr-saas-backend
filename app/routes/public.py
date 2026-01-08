"""
Public Routes (No authentication required)
"""
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import QRCode, QRScan
from datetime import datetime
import user_agents

router = APIRouter(tags=["Public"])


@router.get("/s/{short_code}")
async def scan_qr_code(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for QR code scanning
    Redirects to destination URL and tracks analytics
    """
    
    # Find QR code
    qr_code = db.query(QRCode).filter(QRCode.short_code == short_code).first()
    
    if not qr_code:
        return Response(status_code=404, content="QR code not found")
    
    # Check if QR code can be scanned
    if not qr_code.can_scan:
        return Response(
            status_code=403,
            content="QR code is inactive or expired"
        )
    
    # Extract analytics data
    user_agent_string = request.headers.get("user-agent", "")
    ua = user_agents.parse(user_agent_string)
    
    # Get client IP (handle proxies)
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Determine device type
    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    else:
        device_type = "other"
    
    # Create scan record
    scan = QRScan(
        qr_code_id=qr_code.id,
        ip_address=client_ip,
        user_agent=user_agent_string,
        device_type=device_type,
        os=ua.os.family if ua.os.family else None,
        browser=ua.browser.family if ua.browser.family else None,
        referrer=request.headers.get("referer")
    )
    
    db.add(scan)
    
    # Update QR code stats
    qr_code.total_scans += 1
    qr_code.last_scanned_at = datetime.utcnow()
    
    db.commit()
    
    # Redirect to destination
    return RedirectResponse(url=qr_code.destination_url, status_code=302)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
