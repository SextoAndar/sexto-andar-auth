"""
Application Settings
Centralized configuration management using environment variables with defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings:
    """
    Application configuration - reads environment variables with sane defaults.
    
    Auth service configuration for:
    - API routing (base path)
    - JWT authentication (secret, algorithm, expiration)
    - Database connection (PostgreSQL)
    - SQL debug logging
    """
    
    # Default values
    _API_BASE_PATH: str = "/"
    _JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    _JWT_ALGORITHM: str = "HS256"
    _JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    _PROPERTIES_API_URL: str = "http://localhost:8000"
    _INTERNAL_API_SECRET: str = ""
    
    def __init__(self):
        """Initialize configuration by reading from .env if available."""
        
        # ===== API Configuration =====
        api_base_path = os.getenv("API_BASE_PATH", self._API_BASE_PATH)
        # If empty string, use "/" (root), otherwise strip trailing slashes
        self.API_BASE_PATH: str = "/" if api_base_path == "" else api_base_path.rstrip('/')
        
        # ===== JWT Configuration =====
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", self._JWT_SECRET_KEY)
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", self._JWT_ALGORITHM)
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", str(self._JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        )
        
        # Warn if using default secret
        if self.JWT_SECRET_KEY == self._JWT_SECRET_KEY:
            import warnings
            warnings.warn(
                "⚠️  Using default JWT_SECRET_KEY! Set JWT_SECRET_KEY environment variable in production.",
                category=RuntimeWarning,
                stacklevel=2
            )
        
        # ===== Database Configuration =====
        # Use DATABASE_URL if provided, otherwise build from components
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()
        
        if not self.DATABASE_URL:
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "sexto_andar_db")
            db_user = os.getenv("DB_USER", "sexto_andar_user")
            db_password = os.getenv("DB_PASSWORD", "sexto_andar_pass")
            
            self.DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Database connection retry settings
        self.DB_READY_MAX_ATTEMPTS: int = int(os.getenv("DB_READY_MAX_ATTEMPTS", "30"))
        self.DB_READY_DELAY_SECONDS: float = float(os.getenv("DB_READY_DELAY_SECONDS", "1.0"))
        
        # SQL logging
        self.SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() in ("true", "1", "yes")
        
        # ===== Inter-Service Communication =====
        self.PROPERTIES_API_URL: str = os.getenv("PROPERTIES_API_URL", self._PROPERTIES_API_URL).rstrip('/')
        self.INTERNAL_API_SECRET: str = os.getenv("INTERNAL_API_SECRET", self._INTERNAL_API_SECRET)
        
        # Warn if INTERNAL_API_SECRET is not set
        if not self.INTERNAL_API_SECRET:
            import warnings
            warnings.warn(
                "⚠️  INTERNAL_API_SECRET not set! Inter-service authentication will fail.",
                category=RuntimeWarning,
                stacklevel=2
            )
    
    def api_route(self, route: str) -> str:
        """
        Compose a full route combining API_BASE_PATH + route.
        
        Args:
            route: The route path (e.g., "auth/login" or "/auth/login")
        
        Returns:
            Full route path (e.g., "/api/auth/login" or "/auth/login" if API_BASE_PATH is "/")
        
        Example:
            # With API_BASE_PATH="/api"
            settings.api_route("auth/login") -> "/api/auth/login"
            settings.api_route("/auth/login") -> "/api/auth/login"
            
            # With API_BASE_PATH="/" (root)
            settings.api_route("auth/login") -> "/auth/login"
            settings.api_route("/auth/login") -> "/auth/login"
        """
        if not route:
            return self.API_BASE_PATH
        
        clean_route = route.lstrip('/')
        
        # If API_BASE_PATH is empty or just "/", return route with leading slash
        if not self.API_BASE_PATH or self.API_BASE_PATH == "/":
            return f"/{clean_route}"
        
        return f"{self.API_BASE_PATH}/{clean_route}"


# Global settings instance
settings = Settings()
