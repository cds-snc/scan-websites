LAMBDA_RESOURCES = \
	api \
	scanners/axe-core

TERRAGRUNT_RESOURCES = \
	terragrunt/env/api \
	terragrunt/env/scanners/axe-core \
	terragrunt/env/scanners/owasp-zap

.PHONY: help build dev format fmt install lint migrate migrations
.PHONY: test db-connect terragrunt-apply

help:
	@echo make [COMMAND]
	@echo
	@echo COMMANDS
	@echo "  build             -- Run build commands"
	@echo "  db-connect        -- Create a psql connection to the database"
	@echo "  dev               -- Run API dev server"
	@echo "  format            -- Alias for fmt"
	@echo "  fmt               -- Run formatters"
	@echo "  install           -- Install needed Python and NPM libraries"
	@echo "  install-dev       -- Installs needed development libraries"
	@echo "  lint              -- Run linters"
	@echo "  migrate           -- Alias for migrations"
	@echo "  migations         -- Run migrations"
	@echo "  terragrunt-apply  -- Run the terragrunt-apply command"
	@echo "  test              -- Run tests"

dev:
	$(MAKE) -C api dev

migrate: migrations

migrations:
	$(MAKE) -C api migrations

db-connect:
	psql postgresql://postgres:postgres@db/scan-websites

test: $(addsuffix .test,$(LAMBDA_RESOURCES))

build: $(addsuffix .build,$(LAMBDA_RESOURCES))

format: fmt

fmt: $(addsuffix .fmt,$(LAMBDA_RESOURCES)) $(addsuffix .fmt,$(TERRAGRUNT_RESOURCES))
	@echo "[Formatting terragrunt]"
	$(MAKE) -C terragrunt fmt

install: $(addsuffix .install,$(LAMBDA_RESOURCES))

install-dev: $(addsuffix .install-dev,$(LAMBDA_RESOURCES))

lint: $(addsuffix .lint,$(LAMBDA_RESOURCES))
	@echo "[Linting terragrunt]"
	$(MAKE) -C terragrunt lint

terragrunt-apply: $(addsuffix, .apply,$(TERRAGRUNT_RESOURCES))

define make-rules
.PHONY: $1.test $1.build $1.fmt $1.install $1.install-dev $1.lint

$1.build:
	@echo "[Building $1]"
	$(MAKE) -C $1 build

$1.fmt:
	@echo "[Formatting $1]"
	$(MAKE) -C $1 fmt

$1.install:
	@echo "[Installing $1]"
	$(MAKE) -C $1 install

$1.install-dev:
	@echo "[Installing dev dependencies $1]"
	$(MAKE) -C $1 install-dev

$1.lint:
	@echo "[Linting $1]"
	$(MAKE) -C $1 lint

$1.test:
	@echo "[Testing $1]"
	$(MAKE) -C $1 test
endef
$(foreach component,$(LAMBDA_RESOURCES), $(eval $(call make-rules, $(component))))

define make-terragrunt-rules
.PHONY: $1.apply $1.fmt

$1.apply:
	@echo "[Terragrunt apply $1]"
	$(MAKE) -C $1 apply

$1.fmt:
	@echo "[Formatting $1]"
	$(MAKE) -C $1 fmt
endef
$(foreach component,$(TERRAGRUNT_RESOURCES), $(eval $(call make-rules, $(component))))
