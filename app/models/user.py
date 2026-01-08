"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User role types"""
    USER = "user"
    ADMIN = "admin"


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan types"""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # Subscription
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    qr_codes = relationship("QRCode", back_populates="owner", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="creator")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_premium(self):
        """Check if user has premium subscription"""
        return self.subscription_plan in [SubscriptionPlan.PRO, SubscriptionPlan.BUSINESS]
    
    @property
    def qr_code_limit(self):
        """Get QR code limit based on plan"""
        if self.subscription_plan == SubscriptionPlan.FREE:
            return 3
        return None  # Unlimited for premium
    
    @property
    def scan_limit(self):
        """Get monthly scan limit based on plan"""
        from app.config import settings
        if self.subscription_plan == SubscriptionPlan.FREE:
            return settings.RATE_LIMIT_FREE
        elif self.subscription_plan == SubscriptionPlan.PRO:
            return settings.RATE_LIMIT_PRO
        else:
            return settings.RATE_LIMIT_BUSINESS
