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
    
    def test_api_route_with_empty_string(self):
        """Test api_route with empty string returns base path"""
        from app.settings import settings
        
        assert settings.api_route("") == settings.API_BASE_PATH
    
    def test_api_route_with_multiple_slashes(self):
        """Test api_route removes duplicate slashes"""
        from app.settings import settings
        
        result = settings.api_route("/users")
        assert result == f"{settings.API_BASE_PATH}/users"
        assert "//" not in result or result.startswith("http")
    
    def test_empty_api_base_path_uses_root(self):
        """Test that empty API_BASE_PATH in env results in '/' """
        import os
        original = os.environ.get("API_BASE_PATH")
        
        try:
            # Set empty string
            os.environ["API_BASE_PATH"] = ""
            test_settings = Settings()
            assert test_settings.API_BASE_PATH == "/"
            assert test_settings.api_route("users") == "/users"
        finally:
            # Restore original value
            if original is not None:
                os.environ["API_BASE_PATH"] = original
            elif "API_BASE_PATH" in os.environ:
                del os.environ["API_BASE_PATH"]
    
    def test_settings_all_properties_accessible(self):
        """Test that all settings properties are accessible"""
        from app.settings import settings
        
        # Test all properties can be accessed without error
        _ = settings.API_BASE_PATH
        _ = settings.JWT_SECRET_KEY
        _ = settings.JWT_ALGORITHM
        _ = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        _ = settings.DATABASE_URL
        _ = settings.SQL_DEBUG
        _ = settings.DB_READY_MAX_ATTEMPTS
        _ = settings.DB_READY_DELAY_SECONDS
        
        # All should succeed without exception
        assert True
