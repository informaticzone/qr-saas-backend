"""
QR Code Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime
import secrets
import io
from app.database import get_db
from app.models import User, QRCode, QRScan
from app.utils.auth import get_current_user
from app.services.qr_generator import qr_generator

router = APIRouter(prefix="/qr", tags=["QR Codes"])


# Schemas
class QRCodeCreate(BaseModel):
    title: str
    destination_url: HttpUrl
    is_dynamic: bool = False
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    style: str = "square"
    logo_path: Optional[str] = None


class QRCodeUpdate(BaseModel):
    title: Optional[str] = None
    destination_url: Optional[HttpUrl] = None
    foreground_color: Optional[str] = None
    background_color: Optional[str] = None
    is_active: Optional[bool] = None


class QRCodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    destination_url: str
    short_code: str
    scan_url: str
    is_dynamic: bool
    is_active: bool
    total_scans: int
    foreground_color: str
    background_color: str
    style: str
    created_at: datetime


def generate_short_code() -> str:
    """Generate unique short code for QR"""
    return secrets.token_urlsafe(6)


@router.post("/create", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_qr_code(
    qr_data: QRCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new QR code"""
    
    # Check user's QR limit (for FREE users)
    if not current_user.is_premium:
        qr_count = db.query(QRCode).filter(QRCode.user_id == current_user.id).count()
        if qr_count >= current_user.qr_code_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Free plan limited to {current_user.qr_code_limit} QR codes. Upgrade to PRO for unlimited."
            )
    
    # Generate unique short code
    short_code = generate_short_code()
    while db.query(QRCode).filter(QRCode.short_code == short_code).first():
        short_code = generate_short_code()
    
    # Generate tracking URL
    from app.config import settings
    tracking_url = f"{settings.APP_URL}/s/{short_code}"
    
    # Generate QR code images with tracking URL
    png_bytes, svg_bytes, pdf_bytes = qr_generator.generate(
        data=tracking_url,  # Use tracking URL instead of destination
        foreground_color=qr_data.foreground_color,
        background_color=qr_data.background_color,
        style=qr_data.style,
        logo_path=qr_data.logo_path
    )
    
    # Save files
    file_paths = qr_generator.save_files(short_code, png_bytes, svg_bytes, pdf_bytes)
    
    # Create database record
    new_qr = QRCode(
        user_id=current_user.id,
        title=qr_data.title,
        destination_url=str(qr_data.destination_url),
        short_code=short_code,
        is_dynamic=qr_data.is_dynamic,
        foreground_color=qr_data.foreground_color,
        background_color=qr_data.background_color,
        style=qr_data.style,
        logo_path=qr_data.logo_path,
        file_path_png=file_paths["png"],
        file_path_svg=file_paths["svg"],
        file_path_pdf=file_paths["pdf"]
    )
    
    db.add(new_qr)
    db.commit()
    db.refresh(new_qr)
    
    return new_qr


@router.get("/my-qr-codes", response_model=List[QRCodeResponse])
async def get_my_qr_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all QR codes for current user"""
    qr_codes = db.query(QRCode).filter(QRCode.user_id == current_user.id).all()
    return qr_codes


@router.get("/{qr_id}", response_model=QRCodeResponse)
async def get_qr_code(
    qr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific QR code"""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    return qr_code


@router.put("/{qr_id}", response_model=QRCodeResponse)
async def update_qr_code(
    qr_id: int,
    qr_update: QRCodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update QR code"""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Check if dynamic (can update URL)
    if qr_update.destination_url and not qr_code.is_dynamic:
        raise HTTPException(
            status_code=403,
            detail="Cannot change URL of static QR code. Upgrade to dynamic QR."
        )
    
    # Update fields
    for field, value in qr_update.dict(exclude_unset=True).items():
        setattr(qr_code, field, value)
    
    db.commit()
    db.refresh(qr_code)
    
    return qr_code


@router.delete("/{qr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qr_code(
    qr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete QR code"""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    db.delete(qr_code)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{qr_id}/download/{format}")
async def download_qr_code(
    qr_id: int,
    format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download QR code in specified format (png, svg, pdf)"""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Get file path
    file_path = None
    media_type = None
    
    if format == "png":
        file_path = qr_code.file_path_png
        media_type = "image/png"
    elif format == "svg":
        file_path = qr_code.file_path_svg
        media_type = "image/svg+xml"
    elif format == "pdf":
        file_path = qr_code.file_path_pdf
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use: png, svg, pdf")
    
    if not file_path:
        raise HTTPException(status_code=404, detail=f"Format {format} not available")
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=f"{qr_code.title}.{format}"
    )
