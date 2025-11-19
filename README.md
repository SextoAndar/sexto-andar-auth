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

# Copy environment template and customize if needed
cp .env.example .env

# Edit .env and set JWT_SECRET_KEY for production!
# JWT_SECRET_KEY=your-random-secret-key-here

# Start everything (migration runs automatically)
docker-compose up --build -d
```

The migration will run automatically before the API starts.

**⚠️ IMPORTANT**: Change `JWT_SECRET_KEY` in `.env` before deploying to production!

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

## ⚙️ Configuration

### Environment Variables

All configuration is managed via environment variables. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Key variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_PATH` | `/api` | Base path for all API routes (e.g., `/api/auth/login`) |
| `JWT_SECRET_KEY` | `your-super-secret-key...` | **CRITICAL**: Change in production! Used to sign JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time in minutes |
| `DATABASE_URL` | `postgresql://...` | Full database connection string |
| `SQL_DEBUG` | `false` | Enable SQL query logging (dev only) |
| `DB_READY_MAX_ATTEMPTS` | `30` | Database connection retry attempts |
| `DB_READY_DELAY_SECONDS` | `1.0` | Delay between retry attempts |

**Production checklist:**
- ✅ Set a strong random `JWT_SECRET_KEY`:
  ```bash
  # Generate a secure key
  openssl rand -hex 32
  # or
  python -c "import secrets; print(secrets.token_hex(32))"
  
  # Add to .env
  echo "JWT_SECRET_KEY=<your-generated-key>" >> .env
  ```
- ✅ Use secure database credentials
- ✅ Set appropriate token expiration time
- ✅ Disable `SQL_DEBUG`

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Auth**: JWT with HTTP-only cookies
- **Validation**: Pydantic models
- **Password hashing**: bcrypt
- **Containerization**: Docker Compose
- **Configuration**: Centralized settings module with `.env` support

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

## 📸 Profile Pictures

Users can upload, retrieve, and delete profile pictures stored directly in the database.

### Features
- ✅ Upload images via multipart/form-data
- ✅ Binary storage in PostgreSQL (BYTEA)
- ✅ Supported formats: JPEG, JPG, PNG, GIF
- ✅ Maximum file size: 5MB
- ✅ Public GET endpoint (no authentication required)
- ✅ Automatic content-type handling
- ✅ `hasProfilePicture` flag in user responses

### Endpoints

**Upload Profile Picture** (requires authentication)
```bash
POST /auth/profile/picture
Content-Type: multipart/form-data

curl -X POST http://localhost:8001/auth/profile/picture \
  -H "Cookie: access_token=YOUR_JWT_TOKEN" \
  -F "file=@profile.jpg"

# Response
{
  "message": "Profile picture uploaded successfully",
  "hasProfilePicture": true
}
```

**Get Profile Picture** (public)
```bash
GET /auth/profile/picture/{user_id}

# Use directly in HTML
<img src="http://localhost:8001/auth/profile/picture/{user_id}" alt="Profile" />

# Or download with curl
curl http://localhost:8001/auth/profile/picture/{user_id} -o profile.jpg
```

**Delete Profile Picture** (requires authentication)
```bash
DELETE /auth/profile/picture

curl -X DELETE http://localhost:8001/auth/profile/picture \
  -H "Cookie: access_token=YOUR_JWT_TOKEN"

# Response
{
  "message": "Profile picture deleted successfully",
  "hasProfilePicture": false
}
```

### Frontend Integration

#### 🖼️ Exibindo Foto de Perfil

**A forma mais simples - usar direto na tag `<img>`:**

```html
<!-- Substitua {userId} pelo ID do usuário -->
<img src="http://localhost:8001/auth/profile/picture/019cc49b-f746-4e25-a6dd-425b7d3729be" alt="Profile" />
```

**Em React/Next.js:**

```jsx
// Componente simples
function UserAvatar({ userId }) {
  return (
    <img 
      src={`http://localhost:8001/auth/profile/picture/${userId}`}
      alt="Profile"
      onError={(e) => {
        e.target.src = '/default-avatar.png'; // Fallback se não tiver foto
      }}
    />
  );
}

// Uso
<UserAvatar userId="019cc49b-f746-4e25-a6dd-425b7d3729be" />
```

**Verificar se o usuário tem foto antes de exibir:**

```javascript
// Ao fazer login ou buscar dados do usuário, o campo hasProfilePicture indica se tem foto
const user = await fetch('http://localhost:8001/auth/me', {
  credentials: 'include'
}).then(r => r.json());

// user.hasProfilePicture === true significa que tem foto
// user.hasProfilePicture === false significa que deve usar avatar padrão

// Exemplo de uso condicional
function ProfilePicture({ userId, hasProfilePicture }) {
  if (!hasProfilePicture) {
    return <img src="/default-avatar.png" alt="Default Avatar" />;
  }
  
  return (
    <img 
      src={`http://localhost:8001/auth/profile/picture/${userId}`}
      alt="Profile"
    />
  );
}
```

#### 📤 Upload de Foto (requer autenticação)

```javascript
// Função para fazer upload
async function uploadProfilePicture(fileInput) {
  const file = fileInput.files[0];
  
  // Validação no frontend (opcional mas recomendado)
  if (file.size > 5 * 1024 * 1024) {
    alert('Arquivo muito grande! Máximo 5MB');
    return;
  }
  
  if (!['image/jpeg', 'image/jpg', 'image/png', 'image/gif'].includes(file.type)) {
    alert('Formato inválido! Use JPEG, PNG ou GIF');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8001/auth/profile/picture', {
    method: 'POST',
    credentials: 'include',  // IMPORTANTE: envia o cookie JWT
    body: formData
  });
  
  const result = await response.json();
  
  if (response.ok) {
    console.log('Upload realizado!', result);
    // result.hasProfilePicture === true
    // Recarregar a página ou atualizar o componente
  } else {
    console.error('Erro no upload:', result.detail);
  }
}

// Uso em HTML
<input type="file" accept="image/*" onChange={(e) => uploadProfilePicture(e.target)} />
```

#### 🗑️ Deletar Foto (requer autenticação)

```javascript
async function deleteProfilePicture() {
  const response = await fetch('http://localhost:8001/auth/profile/picture', {
    method: 'DELETE',
    credentials: 'include'  // IMPORTANTE: envia o cookie JWT
  });
  
  const result = await response.json();
  
  if (response.ok) {
    console.log('Foto removida!', result);
    // result.hasProfilePicture === false
    // Atualizar UI para mostrar avatar padrão
  }
}
```

#### 📝 Resumo para o Frontend

**3 informações importantes:**

1. **GET da foto é público** - não precisa de autenticação, use direto na `<img src="...">`
2. **POST (upload) e DELETE precisam de autenticação** - use `credentials: 'include'`
3. **Campo `hasProfilePicture`** - está presente em todos os endpoints que retornam dados do usuário:
   - `/auth/login` → `user.hasProfilePicture`
   - `/auth/me` → `hasProfilePicture`
   - `/auth/register/*` → `hasProfilePicture`
   - `/auth/profile` (após update) → `hasProfilePicture`

**Fluxo completo:**

```javascript
// 1. Usuário faz login
const loginData = await fetch('http://localhost:8001/auth/login', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
}).then(r => r.json());

const userId = loginData.user.id;
const hasPhoto = loginData.user.hasProfilePicture;

// 2. Exibir foto ou avatar padrão
if (hasPhoto) {
  imgElement.src = `http://localhost:8001/auth/profile/picture/${userId}`;
} else {
  imgElement.src = '/default-avatar.png';
}

// 3. Upload quando usuário selecionar arquivo
// (ver código de upload acima)

// 4. Após upload, atualizar UI
// O backend retorna hasProfilePicture: true, então pode atualizar:
imgElement.src = `http://localhost:8001/auth/profile/picture/${userId}`;
```

### Validations
- **File size**: Maximum 5MB
- **File types**: JPEG, JPG, PNG, GIF only
- **Authentication**: Required for upload/delete, not required for GET
- **Storage**: Binary data in PostgreSQL (BYTEA column)

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

### Sharing Postgres Between Projects (recommended)

This repository is configured to *not* create the Postgres instance by default so it can safely use an existing DB already managed by another project (for example `unb/sexto-andar-api`). Key points:

- **Default behavior:** `docker compose up -d` will start the `auth` service without creating Postgres or pgAdmin. This avoids name/port conflicts when another project already runs the database.
- **Full stack (local)**: to let this compose create Postgres, migrations and pgAdmin locally, use the `full-stack` profile:

```bash
# Build and start everything including Postgres and migrations
docker compose --profile full-stack up --build -d
```

- **External network & volume:** the compose is configured to share the network and volume names used by the properties API so both projects can attach to the same Postgres instance:

  - Network name: `sexto-andar-auth_sexto-andar-network`
  - Volume name: `sexto-andar-auth_postgres_data`

  If the other project already created those resources, this compose will attach to them automatically. If needed, create the network manually:

```bash
docker network create sexto-andar-auth_sexto-andar-network
```

- **When running CI** or in environments where you want compose to manage the DB for this project specifically, use the `full-stack` profile shown above.

If you want, I can add a short `docker` section to the `unb/sexto-andar-api` README showing how both projects should be started together.

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
- **Health Check**: http://localhost:8001/api/health
- **Detailed Health**: http://localhost:8001/api/health/detailed
- **Logs**: `docker-compose logs auth`

## 🧪 Testing

### Run tests with Docker:
```bash
docker-compose run --rm test
```

### Run tests locally:
```bash
./run_tests.sh
```

Or using pytest directly:
```bash
python -m pytest tests/ -v
```

### Run with coverage:
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### CI: Run tests in Docker pipeline

Para rodar os testes automaticamente no pipeline de CI/CD, use o perfil `test` do docker-compose:

```bash
# Build sem cache e roda os testes
docker-compose build --no-cache
docker-compose --profile test up --abort-on-container-exit --exit-code-from test

# Limpa depois
docker-compose down --volumes
```

**Exemplo GitHub Actions:**

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Build and test
    run: |
      docker compose build --no-cache
      docker compose --profile test up --abort-on-container-exit --exit-code-from test
```

**Notas:**
- O perfil `test` aguarda o Postgres estar saudável antes de executar
- Exit code != 0 se algum teste falhar (ideal para CI)
- Use `--no-cache` para garantir que a build sempre rode testes atualizados