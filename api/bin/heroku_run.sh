#!/bin/sh
cd /function/db_migrations
SQLALCHEMY_DATABASE_URI=$DATABASE_URL /pymodules/bin/alembic upgrade head
cd ..
SQLALCHEMY_DATABASE_URI=$DATABASE_URL /usr/local/bin/python database/seed.py
SQLALCHEMY_DATABASE_URI=$DATABASE_URL /usr/local/bin/uvicorn main:app --port $PORT