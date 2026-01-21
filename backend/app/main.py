"""
Main FastAPI Application
SaaS Directory Submission Agent
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger

from .config import settings
from .database import init_db
from .routes import (
    saas_products_router,
    directories_router,
    submissions_router,
    dashboard_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Create upload directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "logos"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "screenshots"), exist_ok=True)
    logger.info("Upload directories created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated SaaS directory submission system",
    lifespan=lifespan
)

# Add CORS middleware
# For development, allow all origins if CORS_ORIGINS is "*"
cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"http://localhost(:\d+)?" if cors_origins != ["*"] else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(saas_products_router, prefix="/api")
app.include_router(directories_router, prefix="/api")
app.include_router(submissions_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "saas_products": "/api/saas-products",
            "directories": "/api/directories",
            "submissions": "/api/submissions",
            "dashboard": "/api/dashboard"
        }
    }
