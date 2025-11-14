"""
Pytest configuration and fixtures
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from databases import Database

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "postgresql://sexto_andar_user:sexto_andar_pass@localhost:5432/sexto_andar_test_db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["API_BASE_PATH"] = "/api"
os.environ["SQL_DEBUG"] = "false"

from app.main import app
from app.database.connection import get_db, database
from app.models.base import Base
from app.models.account import Account

# Test database URL
TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "fullName": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "phoneNumber": "11999999999"
    }


@pytest.fixture
def test_property_owner_data():
    """Sample property owner data for testing"""
    return {
        "username": "testowner",
        "fullName": "Test Owner",
        "email": "testowner@example.com",
        "password": "ownerpass123",
        "phoneNumber": "11988888888"
    }


@pytest.fixture
def test_admin_data():
    """Sample admin data for testing"""
    return {
        "username": "testadmin",
        "fullName": "Test Admin",
        "email": "testadmin@example.com",
        "password": "adminpass123",
        "phoneNumber": "11977777777"
    }


@pytest.fixture
def created_user(client: TestClient, test_user_data: dict):
    """Create a test user and return the response"""
    response = client.post("/api/auth/register/user", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_admin(client: TestClient, test_admin_data: dict, db_session: Session):
    """Create a test admin directly in the database"""
    from app.repositories.account_repository import AccountRepository
    from app.models.account import Account, RoleEnum
    from app.auth.password_handler import hash_password
    
    account_repo = AccountRepository(db_session)
    
    # Create admin directly
    admin = Account(
        username=test_admin_data["username"],
        fullName=test_admin_data["fullName"],
        email=test_admin_data["email"],
        phoneNumber=test_admin_data["phoneNumber"],
        password=hash_password(test_admin_data["password"]),
        role=RoleEnum.ADMIN
    )
    
    admin = account_repo.create(admin)
    
    return {
        "id": str(admin.id),
        "username": admin.username,
        "fullName": admin.fullName,
        "email": admin.email,
        "role": admin.role.value,
        "password": test_admin_data["password"]  # Keep password for login
    }


@pytest.fixture
def authenticated_user(client: TestClient, created_user: dict, test_user_data: dict):
    """Create and authenticate a user, return cookies"""
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert login_response.status_code == 200
    return {
        "user": created_user,
        "cookies": login_response.cookies,
        "token": login_response.json()["access_token"]
    }


@pytest.fixture
def authenticated_admin(client: TestClient, created_admin: dict):
    """Create and authenticate an admin, return cookies"""
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": created_admin["username"],
            "password": created_admin["password"]
        }
    )
    assert login_response.status_code == 200
    return {
        "admin": created_admin,
        "cookies": login_response.cookies,
        "token": login_response.json()["access_token"]
    }


@pytest.fixture
def created_property_owner(client: TestClient, test_property_owner_data: dict):
    """Create a test property owner and return the response"""
    response = client.post("/api/auth/register/property-owner", json=test_property_owner_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def authenticated_property_owner(client: TestClient, created_property_owner: dict, test_property_owner_data: dict):
    """Create and authenticate a property owner, return cookies"""
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": test_property_owner_data["username"],
            "password": test_property_owner_data["password"]
        }
    )
    assert login_response.status_code == 200
    return {
        "user": created_property_owner,
        "cookies": login_response.cookies,
        "token": login_response.json()["access_token"]
    }

