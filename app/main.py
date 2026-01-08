"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from .config import settings
from .database import init_db
from .routes import (
    auth_router,
    qr_router,
    analytics_router,
    payments_router,
    public_router,
    admin_router,
    setup_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting QR Code SaaS Platform...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Create storage directories
    os.makedirs(settings.QR_STORAGE_PATH, exist_ok=True)
    print(f"✅ Storage path created: {settings.QR_STORAGE_PATH}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="QR Code Generator SaaS Platform with Analytics and Marketplace",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://192.168.1.2:3000",
        "http://127.0.0.1:3000",
        "https://qr-saas-frontend.vercel.app",
        "https://qr-saas-frontend-3sobmgqpo-informaticzones-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(public_router)  # No prefix for public routes like /s/{code}
app.include_router(auth_router, prefix="/api")
app.include_router(qr_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(setup_router, prefix="/api")

# Static files (for serving QR codes)
if os.path.exists(settings.QR_STORAGE_PATH):
    app.mount("/static/qr", StaticFiles(directory=settings.QR_STORAGE_PATH), name="qr_codes")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - API info"""
    return f"""
    <html>
        <head>
            <title>{settings.APP_NAME} API</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #4F46E5; }}
                .endpoint {{ background: #F3F4F6; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                code {{ background: #1F2937; color: #10B981; padding: 2px 6px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🎯 {settings.APP_NAME} API</h1>
            <p><strong>Version:</strong> {settings.APP_VERSION}</p>
            <p><strong>Environment:</strong> {settings.ENVIRONMENT}</p>
            
            <h2>📚 Documentation</h2>
            <ul>
                <li><a href="/docs">Interactive API Docs (Swagger)</a></li>
                <li><a href="/redoc">Alternative Docs (ReDoc)</a></li>
            </ul>
            
            <h2>🔗 Main Endpoints</h2>
            <div class="endpoint">
                <strong>Authentication:</strong> <code>/api/auth/*</code>
            </div>
            <div class="endpoint">
                <strong>QR Codes:</strong> <code>/api/qr/*</code>
            </div>
            <div class="endpoint">
                <strong>Analytics:</strong> <code>/api/analytics/*</code>
            </div>
            <div class="endpoint">
                <strong>Payments:</strong> <code>/api/payments/*</code>
            </div>
            <div class="endpoint">
                <strong>QR Scan:</strong> <code>/s/{{short_code}}</code>
            </div>
            
            <h2>🚀 Status</h2>
            <p style="color: #10B981; font-weight: bold;">✅ API is running!</p>
        </body>
    </html>
    """


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "qr_codes": "/api/qr",
            "analytics": "/api/analytics",
            "payments": "/api/payments",
            "scan": "/s/{short_code}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
