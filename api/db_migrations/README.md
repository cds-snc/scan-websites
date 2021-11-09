## Migration commands

Create a new automatic migration: `alembic revision --autogenerate -m "create xyz table"`

Create a new migration: `alembic revision -m "create xyz table"`

Run all migrations: `alembic upgrade head`

Get current state: `alembic current`

Revert all migrations: `alembic downgrade base`

Revert last migration: `alembic downgrade -1` or `alembic downgrade {rev_sha}`

## Connect to scan-websites database from devcontainer

`PGPASSWORD=postgres psql -U postgres -h db -d scan-websites`

## Identify postgres foreignkey and unique constraints

```
SELECT conrelid::regclass AS table_from
     , conname
     , pg_get_constraintdef(oid)
FROM   pg_constraint
WHERE  contype IN ('f', 'u ')
AND    connamespace = 'public'::regnamespace  -- your schema here
ORDER  BY conrelid::regclass::text, contype DESC;
```