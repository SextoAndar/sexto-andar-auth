"""
FastAPI Application Documentation Configuration
All API documentation strings and metadata are centralized here.
"""

# API Metadata
API_TITLE = "Auth Service API"
API_VERSION = "1.0.0"

# API Description (shown in /docs and /redoc)
API_DESCRIPTION = """Auth-only service providing account registration, login, logout, and JWT-based session management.

## Authentication
- Registration: Create USER or PROPERTY_OWNER accounts
- Login: Authenticate and receive JWT token in cookie
- Logout: Clear authentication cookie
- Role-based access control via JWT claims

## Technical Stack
- Framework: FastAPI with async/await support
- Database: PostgreSQL with SQLAlchemy ORM
- Authentication: JWT with HTTP-only cookies
- Validation: Pydantic models

## Getting Started
1. Run database migrations: python scripts/migrate_database.py
2. Register using /api/v1/auth/register endpoints
3. Login using /api/v1/auth/login

## Admin Management
Admins can be created via CLI script inside the Docker container:
```bash
docker exec sexto-andar-auth python scripts/create_admin.py <username> <full_name> <email> <password> [phone]
```

## Documentation
- Interactive API docs: /docs (Swagger UI)
- Alternative docs: /redoc (ReDoc)
- OpenAPI schema: /openapi.json
"""

# Server Configuration for API docs
API_SERVERS = [
    {
        "url": "http://localhost:8001",
        "description": "Development server"
    },
    {
        "url": "http://localhost:8001",
        "description": "Docker container"
    }
]

# API Tags for endpoint grouping
API_TAGS_METADATA = [
    {
        "name": "health",
        "description": "Health check and service status endpoints",
    },
    {
        "name": "auth",
        "description": "Authentication and authorization endpoints (login, register, logout)",
    },
    {
        "name": "admin",
        "description": "Admin-only endpoints for user management",
    },
]

# Contact and License info (optional)
API_CONTACT = {
    "name": "SextoAndar Team",
    "url": "https://github.com/SextoAndar/sexto-andar-auth",
}

API_LICENSE_INFO = {
    "name": "MIT",
}
