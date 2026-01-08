"""
Analytics Model - QR Code Scans
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class QRScan(Base):
    """QR Code scan analytics model"""
    __tablename__ = "qr_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    
    # Scan Information
    scanned_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Location Data
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Device Information
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)  # mobile, tablet, desktop
    os = Column(String, nullable=True)  # iOS, Android, Windows, etc.
    browser = Column(String, nullable=True)
    
    # Referrer
    referrer = Column(String, nullable=True)
    
    # Relationship
    qr_code = relationship("QRCode", back_populates="scans")
    
    def __repr__(self):
        return f"<QRScan {self.id} for QR {self.qr_code_id} at {self.scanned_at}>"
