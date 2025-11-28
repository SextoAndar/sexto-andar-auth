from fastapi.testclient import TestClient
import pytest


class TestMeEndpoint:
    """Tests for the /me endpoint"""
    
    def test_me_authenticated(self, client: TestClient, authenticated_user: dict):
        """Test authenticated user can access /me"""
        response = client.get("/api/auth/me", headers=authenticated_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["user"]["username"]
        assert "password" not in data
    
    def test_me_unauthenticated(self, client: TestClient):
        """Test unauthenticated user cannot access /me"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403


class TestLogout:
    """Tests for the /logout endpoint"""
    
    def test_logout_clears_cookie(self, client: TestClient, authenticated_user: dict):
        """Test that logout returns 200 OK"""
        response = client.post("/api/auth/logout") # Logout does not require auth headers
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Successfully logged out"