"""
Tests for Settings configuration
"""
import pytest
import os
from app.settings import Settings


class TestSettings:
    """Test settings configuration"""
    
    def test_settings_loads_from_environment(self):
        """Test that settings loads values from environment variables"""
        from app.settings import settings
        
        assert settings.API_BASE_PATH == "/api"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.SQL_DEBUG is False
    
    def test_settings_jwt_secret_key_exists(self):
        """Test that JWT secret key is set"""
        from app.settings import settings
        
        assert settings.JWT_SECRET_KEY is not None
        assert len(settings.JWT_SECRET_KEY) > 0
    
    def test_settings_database_url_exists(self):
        """Test that database URL is set"""
        from app.settings import settings
        
        assert settings.DATABASE_URL is not None
        assert "postgresql://" in settings.DATABASE_URL
    
    def test_api_route_helper(self):
        """Test the api_route helper method"""
        from app.settings import settings
        
        # Test without leading slash
        assert settings.api_route("users") == "/api/users"
        
        # Test with leading slash
        assert settings.api_route("/users") == "/api/users"
        
        # Test with nested route
        assert settings.api_route("users/profile") == "/api/users/profile"
    
    def test_settings_db_retry_configuration(self):
        """Test database retry configuration"""
        from app.settings import settings
        
        assert isinstance(settings.DB_READY_MAX_ATTEMPTS, int)
        assert settings.DB_READY_MAX_ATTEMPTS > 0
        
        assert isinstance(settings.DB_READY_DELAY_SECONDS, float)
        assert settings.DB_READY_DELAY_SECONDS > 0
