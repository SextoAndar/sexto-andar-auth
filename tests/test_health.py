"""
Tests for health check endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
    assert data["message"] == "Auth Service API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/api/docs"
    assert data["health"] == "/api/health"


def test_health_check_basic(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["api"] == "Auth Service API"
    assert "documentation" in data
    assert "redoc" in data


def test_health_check_detailed(client: TestClient):
    """Test detailed health check endpoint with database status"""
    response = client.get("/api/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "database" in data
    assert "api" in data
    assert "checks" in data
    
    # Check detailed status
    assert data["checks"]["api"] == "running"
    assert data["checks"]["authentication"] == "available"


def test_health_endpoint_no_authentication_required(client: TestClient):
    """Test that health endpoints don't require authentication"""
    # Should work without any cookies or tokens
    response = client.get("/api/health")
    assert response.status_code == 200
    
    response = client.get("/api/health/detailed")
    assert response.status_code == 200
