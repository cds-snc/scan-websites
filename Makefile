.PHONY: dev fmt install lint migrate migrations test db-connect

dev:
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

fmt:
	black . $(ARGS)

install:
	pip3 install --user -r api/requirements.txt

lint:
	pylint .

migrate: migrations

migrations:
	cd api/db_migrations && alembic upgrade head

test:
	cd api && coverage run -m pytest -s -vv tests && coverage report -m

db-connect:
	psql postgresql://postgres:postgres@db/scan-websites