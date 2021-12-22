#!/bin/bash

export DOMAIN_NAME="$HEROKU_APP_NAME".herokuapp.com
env_db=$DATABASE_URL
db="${env_db/postgres/postgresql}"

cd /function/db_migrations
SQLALCHEMY_DATABASE_URI=$db /pymodules/bin/alembic upgrade head
cd ..
SQLALCHEMY_DATABASE_URI=$db python database/seed.py
SQLALCHEMY_DATABASE_URI=$db python -m uvicorn main:app --host 0.0.0.0  --proxy-headers --forwarded-allow-ips="*"  --port $PORT