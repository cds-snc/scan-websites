.PHONY: help build dev fmt install lint migrate migrations test db-connect

TYPESCRIPT_SCANNERS = \
	axe-core

help:
	@echo make [COMMAND]
	@echo
	@echo COMMANDS
	@echo "  build       -- Run build commands"
	@echo "  db-connect  -- Create a psql connection to the database"
	@echo "  dev         -- Run API dev server"
	@echo "  fmt         -- Run formatters"
	@echo "  install     -- install needed Python and NPM libraries"
	@echo "  install-dev -- installs needed development libraries"
	@echo "  lint        -- Run linters"
	@echo "  migrate     -- alias for migrations"
	@echo "  migations   -- Run migrations"
	@echo "  test        -- run tests"

build:
	@for scanner in $(TYPESCRIPT_SCANNERS); do \
		echo "[Building $$scanner]"; \
		cd scanners/$$scanner && npm run build; \
	done;

dev:
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

fmt:
	black . $(ARGS)
	@for scanner in $(TYPESCRIPT_SCANNERS); do \
		echo "[Formatting $$scanner]"; \
		cd scanners/$$scanner && npm run --silent fmt; \
	done;

install-dev:
	pip3 install --user -r api/requirements_dev.txt

install:
	pip3 install --user -r api/requirements.txt
	@for scanner in $(TYPESCRIPT_SCANNERS); do \
		echo "[Installing $$scanner]"; \
		cd scanners/$$scanner && npm ci; \
	done;

lint:
	#pylint .
	@for scanner in $(TYPESCRIPT_SCANNERS); do \
		echo "[Linting $$scanner]"; \
		cd scanners/$$scanner && npm run --silent lint; \
	done;

migrate: migrations

migrations:
	cd api/db_migrations && alembic upgrade head

test:
	cd api && coverage run -m pytest -s -vv tests && coverage report -m
	@for scanner in $(TYPESCRIPT_SCANNERS); do \
		echo "[Testing $$scanner]"; \
		cd scanners/$$scanner && npx jest; \
	done;

db-connect:
	psql postgresql://postgres:postgres@db/scan-websites