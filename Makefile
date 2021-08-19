RESOURCES = \
	api \
	scanners/axe-core \
	scanners/owasp-zap \
	terragrunt

.PHONY: help build dev format fmt install lint migrate migrations fmt-ci lint-ci
.PHONY: test db-connect

help:
	@echo make [COMMAND]
	@echo
	@echo COMMANDS
	@echo "  build       -- Run build commands"
	@echo "  db-connect  -- Create a psql connection to the database"
	@echo "  dev         -- Run API dev server"
	@echo "  format      -- Alias for fmt"
	@echo "  fmt         -- Run formatters"
	@echo "  fmt-ci      -- Run formatters in check mode for CI"
	@echo "  install     -- Install needed Python and NPM libraries"
	@echo "  install-dev -- Installs needed development libraries"
	@echo "  lint        -- Run linters"
	@echo "  lint-ci     -- Run linters in check mode for CI"
	@echo "  migrate     -- Alias for migrations"
	@echo "  migations   -- Run migrations"
	@echo "  test        -- Run tests"

dev:
	$(MAKE) -C api dev

migrate: migrations

migrations:
	$(MAKE) -C api migrations

db-connect:
	psql postgresql://postgres:postgres@db/scan-websites

test: $(addsuffix .test,$(RESOURCES))

build: $(addsuffix .build,$(RESOURCES))

format: fmt

fmt: $(addsuffix .fmt,$(RESOURCES))

fmt-ci: $(addsuffix .fmt-ci,$(RESOURCES))

install: $(addsuffix .install,$(RESOURCES))

install-dev: $(addsuffix .install-dev,$(RESOURCES))

lint: $(addsuffix .lint,$(RESOURCES))

lint-ci: $(addsuffix .lint-ci,$(RESOURCES))

define make-rules

.PHONY: $1.test $1.build $1.fmt $1.install $1.install-dev $1.lint

$1.build:
	@echo "[Building $1]"
	$(MAKE) -C $1 build

$1.fmt:
	@echo "[Formatting $1]"
	$(MAKE) -C $1 fmt

$1.fmt-ci:
	@echo "[Formatting $1]"
	$(MAKE) -C $1 fmt-ci

$1.install:
	@echo "[Installing $1]"
	$(MAKE) -C $1 install

$1.install-dev:
	@echo "[Installing dev dependencies $1]"
	$(MAKE) -C $1 install-dev

$1.lint:
	@echo "[Linting $1]"
	$(MAKE) -C $1 lint

$1.lint-ci:
	@echo "[Linting $1]"
	$(MAKE) -C $1 lint-ci

$1.test:
	@echo "[Testing $1]"
	$(MAKE) -C $1 test
endef
$(foreach component,$(RESOURCES), $(eval $(call make-rules, $(component))))
