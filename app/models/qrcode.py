"""
QR Code Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class QRCode(Base):
    """QR Code model"""
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous
    
    # QR Code Data
    title = Column(String, nullable=False)
    destination_url = Column(Text, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)  # e.g., "abc123"
    
    # Customization
    is_dynamic = Column(Boolean, default=False)  # Can change URL without regenerating
    foreground_color = Column(String, default="#000000")
    background_color = Column(String, default="#FFFFFF")
    logo_path = Column(String, nullable=True)
    style = Column(String, default="square")  # square, rounded, dots
    error_correction = Column(String, default="M")  # L, M, Q, H
    
    # Settings
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # File paths
    file_path_png = Column(String, nullable=True)
    file_path_svg = Column(String, nullable=True)
    file_path_pdf = Column(String, nullable=True)
    
    # Metadata
    custom_metadata = Column(JSON, nullable=True)  # Additional user data
    
    # Analytics summary (cached)
    total_scans = Column(Integer, default=0)
    last_scanned_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="qr_codes")
    scans = relationship("QRScan", back_populates="qr_code", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<QRCode {self.short_code}: {self.title}>"
    
    @property
    def scan_url(self):
        """Get the public scan URL"""
        from app.config import settings
        return f"{settings.APP_URL}/s/{self.short_code}"
    
    @property
    def is_expired(self):
        """Check if QR code is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def can_scan(self):
        """Check if QR code can be scanned"""
        return self.is_active and not self.is_expired
