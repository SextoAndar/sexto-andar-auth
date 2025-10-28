# Auth Service API

FastAPI service focused exclusively on authentication: registration, login, logout, and session management using JWT stored in HTTP-only cookies.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+

### Setup

```bash
git clone <your-repository>
cd sexto-andar-auth

# Start everything (migration runs automatically)
docker-compose up --build -d
```

The migration will run automatically before the API starts.

## 📖 API Documentation

After the service starts, access the complete interactive documentation at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health check**: http://localhost:8001/health

All endpoints, request/response schemas, and examples are available in the Swagger UI.

## 🗄️ Database & Migrations

### Automatic migration

Docker Compose runs migrations automatically:
- ✅ Migration runs before API starts
- ✅ Only executes if database is healthy
- ✅ Migration container stops after completion
- ✅ API only starts after successful migration

### Manual migration (if needed)

```bash
# Run migrations manually
python scripts/migrate_database.py

# Force migrations
python scripts/migrate_database.py --force

# Check status only
python scripts/migrate_database.py --check
```

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Auth**: JWT with HTTP-only cookies
- **Validation**: Pydantic models
- **Password hashing**: bcrypt
- **Containerization**: Docker Compose

## 👨‍💼 Admin Management

### Create First Admin

After starting the containers, create your first admin:

```bash
docker exec sexto-andar-auth python scripts/create_admin.py admin "Admin User" admin@example.com "@Admin11" 11999999999
```

**Validations:**
- Username: 3-50 characters (letters, numbers, underscore)
- Email: valid format and unique
- Password: minimum 8 characters
- Phone: 10-15 digits

### Additional Admins

Once you have an admin, create more via the protected API endpoint. See full documentation at http://localhost:8001/docs

## 🔐 Authentication

### Login Flow
1. Client authenticates via `/api/v1/auth/login`
2. API validates credentials (bcrypt)
3. API generates JWT with claims: `sub`, `username`, `role`
4. JWT returned in response and HTTP-only cookie
5. Client sends JWT on subsequent requests
6. API validates JWT locally (no DB call)

### Available Roles
- **USER**: Regular user
- **PROPERTY_OWNER**: Property owner
- **ADMIN**: System administrator

### Security Features
- ✅ JWT with configurable expiration (default: 30 minutes)
- ✅ HTTP-only cookies (XSS protection)
- ✅ SameSite=Lax (CSRF protection)
- ✅ Bcrypt password hashing
- ✅ Role-based access control
- ✅ Audit logging for admin operations

**All endpoints and usage examples are available in the Swagger UI.**

## ⚙️ Configuration

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

### pgAdmin Access

- **URL**: http://localhost:8080
- **Email**: admin@admin.com
- **Password**: admin

**Database connection:**
- Host: `postgres`
- Port: `5432`
- Database: `sexto_andar_db`
- Username: `sexto_andar_user`
- Password: `sexto_andar_pass`

## 🐳 Docker

### Available Services
- **migrate**: Runs migrations automatically (runs once and stops)
- **auth**: FastAPI application (port 8001)
- **postgres**: PostgreSQL 15 (port 5432)
- **pgadmin**: PostgreSQL web interface (port 8080)

### Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs auth

# Rebuild after code changes
docker-compose up --build -d

# Create admin user
docker exec sexto-andar-auth python scripts/create_admin.py <username> "<full_name>" <email> <password> <phone>
```

## 🔗 Integration with Other Services

Services can validate tokens either:
1. **Locally**: Using the shared `SECRET_KEY` and JWT library
2. **Remotely**: Via the `/api/v1/auth/introspect` endpoint

See the API documentation at http://localhost:8001/docs for integration details.

## 🛠️ Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose logs auth

# Clean restart
docker-compose down -v
docker-compose up --build -d
```

### Database Connection Issues

```bash
# Verify postgres is running
docker-compose ps postgres

# Restart services
docker-compose restart auth
```

### Migration Failures

```bash
# Check migration logs
docker-compose logs migrate

# Force migration manually
docker-compose exec auth python scripts/migrate_database.py --force
```

### Token Issues

- Login again to get a fresh token
- Verify `JWT_EXPIRE_MINUTES` configuration
- Confirm `SECRET_KEY` matches across services

## 📊 Monitoring

- **Basic Status**: http://localhost:8001/
- **Health Check**: http://localhost:8001/health
- **Logs**: `docker-compose logs auth`