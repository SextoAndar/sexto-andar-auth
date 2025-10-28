"""
Tests for authenticated user endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestMeEndpoint:
    """Test /me endpoint for getting current user info"""
    
    def test_me_authenticated(self, client: TestClient, authenticated_user: dict):
        """Test /me endpoint with valid authentication"""
        response = client.get(
            "/api/auth/me",
            cookies=authenticated_user["cookies"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == authenticated_user["user"]["id"]
        assert data["username"] == authenticated_user["user"]["username"]
        assert data["email"] == authenticated_user["user"]["email"]
        assert "password" not in data
    
    def test_me_unauthenticated(self, client: TestClient):
        """Test /me endpoint without authentication fails"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_me_invalid_token(self, client: TestClient):
        """Test /me endpoint with invalid token fails"""
        response = client.get(
            "/api/auth/me",
            cookies={"access_token": "invalid-token"}
        )
        
        assert response.status_code == 401


class TestLogout:
    """Test logout endpoint"""
    
    def test_logout_success(self, client: TestClient, authenticated_user: dict):
        """Test successful logout"""
        response = client.post(
            "/api/auth/logout",
            cookies=authenticated_user["cookies"]
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_logout_unauthenticated(self, client: TestClient):
        """Test logout without authentication (should still work)"""
        response = client.post("/api/auth/logout")
        
        # Logout should work even without auth
        assert response.status_code == 200


class TestTokenIntrospection:
    """Test token introspection endpoint"""
    
    def test_introspect_valid_token(self, client: TestClient, authenticated_user: dict):
        """Test introspection with valid token"""
        response = client.post(
            "/api/auth/introspect",
            json={"token": authenticated_user["token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active"] is True
        assert "claims" in data
        assert data["claims"]["username"] == authenticated_user["user"]["username"]
        assert data["claims"]["role"] == "USER"
        assert "sub" in data["claims"]  # User ID
        assert "exp" in data["claims"]  # Expiration
    
    def test_introspect_invalid_token(self, client: TestClient):
        """Test introspection with invalid token"""
        response = client.post(
            "/api/auth/introspect",
            json={"token": "invalid.token.here"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active"] is False
        assert "reason" in data
    
    def test_introspect_missing_token(self, client: TestClient):
        """Test introspection without token"""
        response = client.post(
            "/api/auth/introspect",
            json={}
        )
        
        assert response.status_code == 422
