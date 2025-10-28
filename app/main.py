"""
FastAPI Application Main File
Real Estate Management API
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
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

# CORS middleware (adjust for your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/", tags=["health"], summary="Root Health Check")
async def root():
    """Root endpoint health check. Returns basic API information and status."""
    return {
        "message": "Auth Service API is running",
        "status": "healthy",
        "version": API_VERSION,
        "api": API_TITLE,
        "documentation": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["health"], summary="Detailed Health Check")
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

# API Routes will be added here
# Example structure:
# app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
# app.include_router(properties.router, prefix="/api/v1/properties", tags=["Properties"])
# app.include_router(visits.router, prefix="/api/v1/visits", tags=["Visits"])
# app.include_router(proposals.router, prefix="/api/v1/proposals", tags=["Proposals"])

# Include API Routes (auth only)
app.include_router(auth_router, prefix="/api/v1")

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
