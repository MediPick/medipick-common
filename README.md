# MediPick Core (`medipick-core`)

Unified Core Library for the MediPick Healthcare Platform:
- **Database Models**: Canonical SQLAlchemy 2.0 async models for all tables.
- **Migrations**: Single source of truth for Alembic database migrations.
- **Domain Enums**: Order FSM states, user roles, staff permissions, and statuses.
- **Security Utilities**: Password hashing, JWT token generation & verification.
- **Core Schemas**: Standard API response envelopes and core output DTOs.

## Installation

### Local Development (Editable Mode)
```bash
pip install -e ./medipick-core
```

### In Docker
```dockerfile
COPY medipick-core /app/medipick-core
RUN pip install --no-cache-dir -e /app/medipick-core
```

### Git Dependency
```bash
pip install "git+https://github.com/medipick-lk/medipick-core.git@main"
```

## Structure
- `medipick_core/database.py`: Async engine, sessionmaker, and `get_db` generator.
- `medipick_core/models/`: Declarative ORM models (`Order`, `User`, `Pharmacy`, etc.).
- `medipick_core/enums/`: Unified system enums.
- `medipick_core/schemas/`: Shared Pydantic response models.
- `medipick_core/security/`: Cryptographic hashing and JWT helpers.
- `alembic/`: Unified database migrations.
