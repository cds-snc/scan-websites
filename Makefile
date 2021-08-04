.PHONY: help build dev fmt install lint migrate migrations
.PHONY: test db-connect

RESOURCES = \
	api \
	scanners/axe-core

help:
	@echo make [COMMAND]
	@echo
	@echo COMMANDS
	@echo "  build       -- Run build commands"
	@echo "  db-connect  -- Create a psql connection to the database"
	@echo "  dev         -- Run API dev server"
	@echo "  fmt         -- Run formatters"
	@echo "  install     -- Install needed Python and NPM libraries"
	@echo "  install-dev -- Installs needed development libraries"
	@echo "  lint        -- Run linters"
	@echo "  migrate     -- Alias for migrations"
	@echo "  migations   -- Run migrations"
	@echo "  test        -- Run tests"

build:
	@for item in $(RESOURCES); do \
		echo "[Building $$item]"; \
		make -C $$item build; \
	done;

dev:
	make -C api dev

fmt:
	@for item in $(RESOURCES); do \
		echo "[Formatting $$item]"; \
		make -C $$item fmt; \
	done;

install:
	@for item in $(RESOURCES); do \
		echo "[Installing $$item]"; \
		make -C $$item install; \
	done;

install-dev:
	@for item in $(RESOURCES); do \
		echo "[Installing dev dependencies $$item]"; \
		make -C $$item install-dev; \
	done;

lint:
	@for item in $(RESOURCES); do \
		echo "[Linting $$item]"; \
		make -C $$item lint; \
	done;

migrate: migrations

migrations:
	make -C api migrations

test:
	@for item in $(RESOURCES); do \
		echo "[Testing $$item]"; \
		make -C $$item test; \
	done;

db-connect:
	psql postgresql://postgres:postgres@db/scan-websites