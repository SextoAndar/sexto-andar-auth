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
    initialize_database, 
    check_database_connection
)

# Import models (this ensures they are registered with SQLAlchemy)
from app.models import Account, Property, Address, Visit, Proposal

# Import controllers/routers
from app.controllers.auth_controller import router as auth_router
from app.controllers.admin_controller import router as admin_router

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
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting FastAPI application...")
    
    try:
        # Connect to database
        await connect_db()
        
        # Initialize database (validate models and create tables)
        success = await initialize_database()
        if not success:
            logger.error("❌ Failed to initialize database. Shutting down...")
            sys.exit(1)
            
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        sys.exit(1)
        
    yield  # Application runs here
    
    # Shutdown
    logger.info("🔄 Shutting down application...")
    try:
        await disconnect_db()
        logger.info("✅ Application shutdown completed")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Create FastAPI application
app = FastAPI(
    title="Real Estate Management API",
    description="API for managing real estate properties, accounts, visits, and proposals",
    version="1.0.0",
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

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Real Estate Management API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check including database connectivity"""
    try:
        # Check database connection
        db_healthy = await check_database_connection()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "api": "running"
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

# Include API Routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌟 Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
