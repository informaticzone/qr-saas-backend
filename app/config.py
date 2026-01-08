"""
Application Configuration
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Info
    APP_NAME: str = "QR Code Pro"
    APP_VERSION: str = "1.0.0"
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./qr_saas.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_SETUP_KEY: str = "setup-admin-2026-change-me"  # Change in production
    
    # Stripe
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PRO: str = ""
    STRIPE_PRICE_ID_BUSINESS: str = ""
    
    # Email
    EMAIL_SERVICE: str = "sendgrid"
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@qrcodepro.com"
    FROM_NAME: str = "QR Code Pro"
    
    # QR Code Settings
    QR_MAX_SIZE: int = 2048
    QR_DEFAULT_ERROR_CORRECTION: str = "M"
    QR_STORAGE_PATH: str = "./storage/qrcodes"
    
    # Analytics
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    META_PIXEL_ID: Optional[str] = None
    
    # Rate Limiting (scans per month)
    RATE_LIMIT_FREE: int = 100
    RATE_LIMIT_PRO: int = 10000
    RATE_LIMIT_BUSINESS: int = 100000
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_LOGO_FORMATS: str = "png,jpg,jpeg,svg"
    
    # Plans
    PLAN_FREE_QR_LIMIT: int = 3
    PLAN_PRO_PRICE: float = 9.90
    PLAN_BUSINESS_PRICE: float = 29.00
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
