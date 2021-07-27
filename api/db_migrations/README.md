## Migration commands

Create a new migration: `alembic revision -m "create xyz table"`

Run all migrations: `alembic upgrade head`

Get current state: `alembic current`

Revert all migrations: `alembic downgrade base`

Revert last migration: `alembic downgrade -1` or `alembic downgrade {rev_sha}`