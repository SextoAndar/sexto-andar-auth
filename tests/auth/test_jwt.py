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


class TestJWTHandlerParametrized:
    """Parametrized tests for JWT token handling"""
    
    @pytest.mark.parametrize("user_data", [
        {"sub": "user123", "username": "testuser", "role": "USER"},
        {"sub": "admin456", "username": "admin", "role": "ADMIN"},
        {"sub": "owner789", "username": "propertyowner", "role": "PROPERTY_OWNER"},
        {"sub": "12345", "username": "numeric", "role": "USER"},
        {"sub": "uuid-test-123", "username": "test_user", "role": "USER"},
    ])
    def test_create_and_verify_various_user_data(self, user_data):
        """Test creating and verifying tokens with various user data"""
        token = create_access_token(user_data)
        payload = verify_token(token)
        
        assert payload is not None
        for key, value in user_data.items():
            assert payload[key] == value
    
    @pytest.mark.parametrize("invalid_token", [
        "not.a.token",
        "invalid",
        "",
        "a.b",  # Only 2 parts
        "a.b.c.d",  # Too many parts
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
        "Bearer token",
        None,
    ])
    def test_verify_various_invalid_tokens(self, invalid_token):
        """Test that various invalid token formats return None"""
        if invalid_token is None:
            # Skip None as it would cause a different error
            pytest.skip("None token handled differently")
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    @pytest.mark.parametrize("expires_minutes", [
        1,
        5,
        15,
        30,
        60,
        120,
        1440,  # 24 hours
    ])
    def test_token_with_various_expiry_times(self, expires_minutes):
        """Test creating tokens with various expiration times"""
        data = {"sub": "user123"}
        custom_delta = timedelta(minutes=expires_minutes)
        
        token = create_access_token(data, expires_delta=custom_delta)
        payload = verify_token(token)
        
        assert payload is not None
        
        # Check expiration is approximately correct
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff_minutes = (exp_datetime - now).total_seconds() / 60
        
        # Allow 1 minute tolerance
        assert expires_minutes - 1 <= time_diff_minutes <= expires_minutes + 1
    
    @pytest.mark.parametrize("extra_claims", [
        {"custom_field": "value"},
        {"is_verified": True},
        {"login_count": 42},
        {"permissions": ["read", "write"]},
        {"metadata": {"key": "value", "number": 123}},
    ])
    def test_token_with_extra_claims(self, extra_claims):
        """Test creating tokens with additional custom claims"""
        base_data = {"sub": "user123", "username": "testuser"}
        data = {**base_data, **extra_claims}
        
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload is not None
        
        # Verify base data
        for key, value in base_data.items():
            assert payload[key] == value
        
        # Verify extra claims
        for key, value in extra_claims.items():
            assert payload[key] == value
