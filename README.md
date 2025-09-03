# Real Estate Management API

A FastAPI-based real estate management system with PostgreSQL database and SQLAlchemy models.

## 🏗️ Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy 2.0**: Modern ORM with async support
- **Docker**: Containerized database environment
- **Pydantic**: Data validation and serialization

## 📋 Models

The API includes the following database models:

- **Account**: User accounts with role-based access (USER/PROPERTY_OWNER)
- **Property**: Real estate properties with type, pricing, and location
- **Address**: Address information with Brazilian postal code validation
- **Visit**: Visit scheduling system with date validations
- **Proposal**: Property purchase/rental proposals with status management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git (optional, for cloning)

### Installation & Running

1. **Clone and start everything**:
   ```bash
   git clone <repository>
   cd sexto-andar-api
   docker-compose up --build -d
   ```

   This will:
   - Build the FastAPI Docker image
   - Start PostgreSQL container
   - Start FastAPI container
   - Start pgAdmin container
   - Wait for database to be ready
   - Automatically create all tables

### Commands

```bash
# Start all services (build + run in background)
docker-compose up --build -d

# Start and show logs (foreground)
docker-compose up --build

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down --volumes
```

## 🔍 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check with database status

### API Documentation
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🗄️ Database

The application automatically:
1. **Connects** to PostgreSQL on startup
2. **Validates** all SQLAlchemy models
3. **Creates** database tables if they don't exist
4. **Logs** the entire initialization process

### Database Access

- **Database**: sexto_andar_db
- **Host**: localhost:5432
- **User**: sexto_andar_user
- **Password**: sexto_andar_pass

### pgAdmin Access
- **URL**: http://localhost:8080
- **Email**: admin@sextoandar.com
- **Password**: admin123

## 🛠️ Development

### Docker Commands

```bash
# Start all services
docker-compose up --build -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f postgres

# Rebuild after code changes
docker-compose up --build -d api

# Check service status
docker-compose ps
```

### Local Development (optional)

If you prefer to run the API locally for development:

```bash
# Start only PostgreSQL
docker-compose up -d postgres

# Run API locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## 📁 Project Structure

```
sexto-andar-api/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py          # Database configuration and BaseModel
│   ├── models/
│   │   ├── __init__.py            # Model imports
│   │   ├── account.py             # User accounts
│   │   ├── property.py            # Real estate properties
│   │   ├── address.py             # Address information
│   │   ├── visit.py               # Visit scheduling
│   │   └── proposal.py            # Purchase/rental proposals
│   └── main.py                    # FastAPI application
├── Dockerfile                     # Docker configuration for API
├── docker-compose.yml             # Multi-container Docker setup
├── .dockerignore                  # Docker ignore file
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## ✅ Features

- **Full Docker Setup**: PostgreSQL, FastAPI, and pgAdmin all in containers
- **Automatic Database Setup**: PostgreSQL starts empty, SQLAlchemy creates all tables
- **Model Validation**: All models are validated on startup
- **Health Checks**: API and database health monitoring
- **Auto-reload**: Development server with automatic code reloading (when running locally)
- **Container Orchestration**: Easy start/stop with single commands
- **Comprehensive Logging**: Detailed startup and operation logs
- **Production Ready**: Dockerfile with security best practices

## 🧪 Testing

Test the API endpoints:

```bash
# Start services
docker-compose up -d

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# Open API documentation
open http://localhost:8000/docs
```

## 🔧 Configuration

### Environment Variables

The application uses these default configurations (defined in `docker-compose.yml`):

```bash
# PostgreSQL Database
POSTGRES_DB=sexto_andar_db
POSTGRES_USER=sexto_andar_user
POSTGRES_PASSWORD=sexto_andar_pass
DATABASE_URL=postgresql://sexto_andar_user:sexto_andar_pass@postgres:5432/sexto_andar_db

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@sextoandar.com
PGADMIN_DEFAULT_PASSWORD=admin123

# API Settings
SQL_DEBUG=false  # Set to "true" to enable SQL query logging
```

To customize these values, you can:
1. Edit `docker-compose.yml` directly
2. Create a `.env` file in the root directory
3. Set environment variables before running Docker Compose

## 📦 Dependencies

Key packages:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM
- `sqlalchemy-utils`: Additional field types
- `databases`: Async database support
- `asyncpg`: PostgreSQL async driver
- `psycopg2-binary`: PostgreSQL sync driver

## 🎯 Next Steps

The foundation is complete! You can now:

1. **Add API Routes**: Create endpoints for CRUD operations
2. **Implement Authentication**: Add JWT or session-based auth
3. **Add Business Logic**: Implement property search, filtering, etc.
4. **Add Tests**: Unit and integration tests
5. **Deploy**: Production deployment with Docker

---

**Ready to build your real estate management system!** 🏠✨Servidor Backend do projeto de TPEE - UnB
