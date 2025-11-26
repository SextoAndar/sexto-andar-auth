"""
FastAPI Application Main File
Real Estate Management API
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import database functions
from app.database.connection import (
    connect_db, 
    disconnect_db, 
    check_database_connection,
    wait_for_database_ready
)

# Import models (register only auth-related models)
from app.models import Account

# Import controllers/routers (auth only)
from app.controllers.auth_controller import router as auth_router
from app.controllers.admin_controller import router as admin_router

# Import API documentation configuration
from app.config.api_docs import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    API_SERVERS,
    API_TAGS_METADATA,
    API_CONTACT,
    API_LICENSE_INFO
)

# Import settings
from app.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting FastAPI application...")
    
    try:
        # Wait for DB to be ready (shared DB may already be up)
        if not await wait_for_database_ready():
            logger.error("Database connection failed. Please run migration script first.")
            logger.error("Run: python scripts/migrate_database.py")
            sys.exit(1)
        # ensure connection handle is open
        await connect_db()
            
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)
        
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await disconnect_db()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Create FastAPI application with professional documentation
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    servers=API_SERVERS,
    openapi_tags=API_TAGS_METADATA,
    contact=API_CONTACT,
    license_info=API_LICENSE_INFO,
    lifespan=lifespan
)

# Custom Exception Handler for ValueError
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Handles ValueError exceptions, which are often raised for validation errors
    that are not covered by Pydantic. This prevents them from becoming 500 errors.
    """
    logger.error(f"Validation error occurred: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# CORS middleware (adjust for your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sexto-andar-api-3ef30ad16a1f.herokuapp.com/",
        "https://sexto-andar-auth-6def0cff0560.herokuapp.com/",
        "https://sexto-andar-dev-proxy-d6d02970f88a.herokuapp.com/",
        "https://sexto-andar-web-9a6357fcb391.herokuapp.com/"
    ],  # Frontend URLs - add your production URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API Router with base path
api_router = APIRouter(prefix=settings.API_BASE_PATH)

# Health check endpoints under api_router
@api_router.get("/health", tags=["health"], summary="Root Health Check")
async def health_root():
    """Root endpoint health check. Returns basic API information and status."""
    return {
        "message": "Auth Service API is running",
        "status": "healthy",
        "version": API_VERSION,
        "api": API_TITLE,
        "documentation": f"{settings.API_BASE_PATH}/docs",
        "redoc": f"{settings.API_BASE_PATH}/redoc"
    }

@api_router.get("/health/detailed", tags=["health"], summary="Detailed Health Check")
async def health_check():
    """Comprehensive health check including database connectivity status."""
    try:
        # Check database connection
        db_healthy = await check_database_connection()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "api": "running",
            "checks": {
                "database": "connected" if db_healthy else "disconnected",
                "api": "running",
                "authentication": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Include all API routes under the api_router
# Auth router has prefix="/auth" internally, so full path will be {API_BASE_PATH}/auth/*
# Example: with API_BASE_PATH="/api" -> /api/auth/login, /api/auth/register/user, etc.
api_router.include_router(auth_router)
api_router.include_router(admin_router)

# Example structure for adding more routers:
# api_router.include_router(accounts_router)
# api_router.include_router(properties_router)

# Include the main API router in the app
app.include_router(api_router)

# Root endpoint - Simple redirect or info
@app.get("/", tags=["root"], summary="API Root", include_in_schema=False)
async def root():
    """Root endpoint - Returns API information."""
    return {
        "message": "Auth Service API",
        "version": API_VERSION,
        "docs": f"{settings.API_BASE_PATH}/docs",
        "health": f"{settings.API_BASE_PATH}/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
