#!/bin/sh
cd /function/db_migrations
SQLALCHEMY_DATABASE_URI=$DATABASE_URL /pymodules/bin/alembic upgrade head
cd ..
SQLALCHEMY_DATABASE_URI=$DATABASE_URL python database/seed.py
SQLALCHEMY_DATABASE_URI=$DATABASE_URL python -m uvicorn main:app --port $PORT