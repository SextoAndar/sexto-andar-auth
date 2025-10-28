# Scripts

This folder contains utility scripts for the authentication service.

## migrate_database.py

Script for applying and validating database migrations.

### Usage

```bash
# Run migrations interactively
python scripts/migrate_database.py

# Force migrations (no prompts)
python scripts/migrate_database.py --force

# Check DB status only
python scripts/migrate_database.py --check
```

### When to use
- First installation: run before starting the application for the first time
- After model changes: run when you modify ORM models
- Sync issues: run when the DB schema is out of sync

### What the script does
1. Validate SQLAlchemy models
2. Apply schema migrations
3. Create/update tables
4. Check DB connectivity

## create_admin.py

Script to create administrative users.

### Usage

```bash
# Create an admin user
python scripts/create_admin.py <username> "<full_name>" <email> <password> <phone>
```

### When to use
- To create the first administrator account
- To create additional admin accounts when needed

## Recommended execution order

1. Automatic / normal usage:

```bash
# Start services (migrations run automatically)
docker-compose up --build -d

# Create admin if necessary
python scripts/create_admin.py <username> "<full_name>" <email> <password> <phone>
```

2. First install (manual control):

```bash
# 1) Start Postgres
docker-compose up -d postgres

# 2) Run migrations manually
python scripts/migrate_database.py

# 3) Create admin (optional)
python scripts/create_admin.py <username> "<full_name>" <email> <password> <phone>

# 4) Start the app
docker-compose up -d
```

## Notes

- ✅ Automatic migrations: Docker Compose runs `migrate_database.py` automatically
- ✅ Scripts available for special cases and debugging
- ✅ Service starts only after migrations complete successfully
- ⚠️ Use `--build` when you change application code to rebuild images
