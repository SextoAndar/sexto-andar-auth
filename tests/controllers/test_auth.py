"""
Tests for authentication endpoints (register and login)
"""
import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_user_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration"""
        response = client.post("/api/auth/register/user", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["username"] == test_user_data["username"]
        assert data["fullName"] == test_user_data["fullName"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == "USER"
        assert "password" not in data  # Password should not be returned
        assert "created_at" in data
    
    def test_register_user_duplicate_username(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate username fails"""
        # First registration
        response1 = client.post("/api/auth/register/user", json=test_user_data)
        assert response1.status_code == 201
        
        # Second registration with same username
        response2 = client.post("/api/auth/register/user", json=test_user_data)
        assert response2.status_code == 400
        assert "username already exists" in response2.json()["detail"].lower()
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate email fails"""
        # First registration
        response1 = client.post("/api/auth/register/user", json=test_user_data)
        assert response1.status_code == 201
        
        # Second registration with same email, different username
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_user"
        response2 = client.post("/api/auth/register/user", json=duplicate_data)
        assert response2.status_code == 400
        assert "email already exists" in response2.json()["detail"].lower()
    
    def test_register_user_invalid_email(self, client: TestClient, test_user_data: dict):
        """Test registration with invalid email fails"""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "not-an-email"
        
        response = client.post("/api/auth/register/user", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_password(self, client: TestClient, test_user_data: dict):
        """Test registration with short password fails"""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "short"
        
        response = client.post("/api/auth/register/user", json=invalid_data)
        assert response.status_code == 422
    
    def test_register_user_missing_fields(self, client: TestClient):
        """Test registration with missing required fields fails"""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # Missing password, fullName, phoneNumber
        }
        
        response = client.post("/api/auth/register/user", json=incomplete_data)
        assert response.status_code == 422


class TestPropertyOwnerRegistration:
    """Test property owner registration endpoints"""
    
    def test_register_property_owner_success(self, client: TestClient, test_property_owner_data: dict):
        """Test successful property owner registration"""
        response = client.post("/api/auth/register/property-owner", json=test_property_owner_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["username"] == test_property_owner_data["username"]
        assert data["role"] == "PROPERTY_OWNER"
        assert "password" not in data


class TestLogin:
    """Test login endpoints"""
    
    def test_login_success(self, client: TestClient, created_user: dict, test_user_data: dict):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_login_wrong_password(self, client: TestClient, created_user: dict, test_user_data: dict):
        """Test login with wrong password fails"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user fails"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials fails"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422
