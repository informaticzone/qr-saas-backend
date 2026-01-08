"""
Routes package initialization
"""
from .auth import router as auth_router
from .qr import router as qr_router
from .analytics import router as analytics_router
from .payments import router as payments_router
from .public import router as public_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "qr_router",
    "analytics_router",
    "payments_router",
    "public_router",
    "admin_router",
]
