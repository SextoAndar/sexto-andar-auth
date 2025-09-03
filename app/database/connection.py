"""
Database configuration for FastAPI with SQLAlchemy
"""

import os
import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, MetaData, inspect, Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
from databases import Database

# Database configurations
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://sexto_andar_user:sexto_andar_pass@localhost:5432/sexto_andar_db"
)

# For async connections
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Avoids connection issues in containers
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"  # Log SQL queries if SQL_DEBUG=true
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

# Base model class with common fields
class BaseModel(Base):
    """
    Base class for all models.
    Includes common fields like ID, timestamps, etc.
    """
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()")
    )
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()")
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()")
    )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

# Metadata configuration
metadata = MetaData()

# Database instance for async operations
database = Database(DATABASE_URL)

# Dependency to get database session
def get_db():
    """
    Dependency that provides a database session.
    Use with Depends() in FastAPI routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async function to connect to database
async def connect_db():
    """Connect to database (use on application startup)"""
    await database.connect()
    logging.info("✅ Connected to PostgreSQL database")

# Async function to disconnect from database
async def disconnect_db():
    """Disconnect from database (use on application shutdown)"""
    await database.disconnect()
    logging.info("📴 Disconnected from PostgreSQL database")

# Function to create all tables
def create_tables():
    """Create all tables defined in models"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("🗄️  Tables created/verified successfully")
        return True
    except SQLAlchemyError as e:
        logging.error(f"❌ Error creating tables: {e}")
        return False

# Function to validate models
def validate_models():
    """Validate all SQLAlchemy models"""
    try:
        # Import all models to ensure they're registered with Base
        from ..models import account, property, address, visit, proposal
        
        # Get inspector to check database structure
        inspector = inspect(engine)
        
        # Validate that all models are properly configured
        for table in Base.metadata.tables.values():
            logging.info(f"✅ Model validated: {table.name}")
            
        # Check if we can create a session
        session = SessionLocal()
        session.close()
        
        logging.info("✅ All models validated successfully")
        return True
        
    except Exception as e:
        logging.error(f"❌ Model validation error: {e}")
        return False

# Function to initialize database
async def initialize_database():
    """Initialize database: connect, validate models, create tables"""
    try:
        logging.info("🔄 Initializing database...")
        
        # Test connection first
        if not await check_database_connection():
            return False
            
        # Validate models
        if not validate_models():
            return False
            
        # Create tables if they don't exist
        if not create_tables():
            return False
            
        logging.info("✅ Database initialization completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        return False

# Function to check connection
async def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        if not database.is_connected:
            await database.connect()
        await database.fetch_val("SELECT 1")
        return True
    except Exception as e:
        logging.error(f"❌ Database connection error: {e}")
        return False
