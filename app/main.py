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
    title="Auth Service API",
    description="""Auth-only service providing account registration, login, logout, and JWT-based session management.

## Authentication
- Registration: Create USER or PROPERTY_OWNER accounts
- Login: Authenticate and receive JWT token in cookie
- Logout: Clear authentication cookie
- Role-based access control via JWT claims

## Technical Stack
- Framework: FastAPI with async/await support
- Database: PostgreSQL with SQLAlchemy ORM
- Authentication: JWT with HTTP-only cookies
- Validation: Pydantic models

## Getting Started
1. Run database migrations: python scripts/migrate_database.py
2. Register using /api/v1/auth/register endpoints
3. Login using /api/v1/auth/login
""",
    version="1.0.0",
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ],
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
        "version": "1.0.0",
        "api": "Auth Service API",
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
