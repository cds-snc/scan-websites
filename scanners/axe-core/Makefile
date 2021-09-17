.PHONY: build fmt install install-dev lint test fmt-ci lint-ci

build:
	npm run build

fmt:
	npm run --silent fmt

install:
	npm ci

install-dev:
	npm install --also=dev

lint:
	npm run --silent lint

lint: ci
	npm run lint:ci

test:
	npx jest

fmt-ci:
	npm run fmt:ci