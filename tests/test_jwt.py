"""
Tests for JWT token functionality
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.auth.jwt_handler import create_access_token, verify_token, get_token_expiry


class TestJWTHandler:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test creating a valid access token"""
        data = {
            "sub": "user123",
            "username": "testuser",
            "role": "USER"
        }
        
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2  # JWT has 3 parts separated by dots
    
    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        data = {
            "sub": "user123",
            "username": "testuser",
            "role": "USER"
        }
        
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["role"] == "USER"
        assert "exp" in payload
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token returns None"""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        
        assert payload is None
    
    def test_token_with_custom_expiry(self):
        """Test creating token with custom expiration time"""
        data = {"sub": "user123"}
        custom_delta = timedelta(minutes=60)
        
        token = create_access_token(data, expires_delta=custom_delta)
        payload = verify_token(token)
        
        assert payload is not None
        # Check that expiration is approximately 60 minutes from now
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = (exp_datetime - now).total_seconds()
        
        # Should be close to 3600 seconds (60 minutes)
        assert 3500 < time_diff < 3700
    
    def test_get_token_expiry(self):
        """Test getting default token expiry"""
        expiry = get_token_expiry()
        
        assert isinstance(expiry, timedelta)
        assert expiry.total_seconds() > 0
    
    def test_token_contains_expiration(self):
        """Test that created tokens contain expiration field"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
        
        # Expiration should be in the future
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now_timestamp
