# Auth Service API

Auth-only service providing account registration, login, logout, and JWT-based session management.

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

1. Run database migrations: `python scripts/migrate_database.py`
2. Register using `/api/v1/auth/register` endpoints
3. Login using `/api/v1/auth/login`

## How the flow works (high level)

1. The client sends credentials to `/api/v1/auth/login`.
2. The API validates the credentials (passwords hashed with bcrypt).
3. On success the API creates a JWT access token with user claims and sets it as an HTTP-only cookie.
4. Subsequent requests include the cookie; server-side dependencies validate and decode the JWT to authorize the request.
5. For administrative operations, the token must include an ADMIN role claim and pass role checks.

## Migrations

Migrations are handled by the `scripts/migrate_database.py` script. The Docker Compose setup runs a `migrate` service that executes this script before the API starts, ensuring the schema is ready.

### Manual migration (if needed)

Run:

```bash
python scripts/migrate_database.py
```

To force migrations without prompts:

```bash
python scripts/migrate_database.py --force
```

## Admin management

- A bootstrap script `scripts/create_admin.py` is available to create an initial administrator account from inside the container or locally.
- Admins can create/delete other admins via admin-only endpoints; the service includes safeguards (cannot delete yourself, cannot delete the last admin).

## Troubleshooting

- If migrations fail, check migration logs:

```bash
docker-compose logs migrate
```

- To run migrations interactively inside the `auth` container:

```bash
docker-compose exec auth python scripts/migrate_database.py --force
```

## Notes

- The API exposes OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).
- Keep the `docs/` folder for larger documents and architecture notes. This `API.md` is the canonical place for the long description used by developers.
