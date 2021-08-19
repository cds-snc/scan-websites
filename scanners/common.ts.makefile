.PHONY: build fmt fmt-ci install install-dev lint lint-ci test

build:
	npm run build

fmt:
	npm run --silent fmt

fmt-ci:
	npm run fmt:ci

install:
	npm ci

install-dev:

lint:
	npm run --silent lint

lint-ci:
	npm run lint:ci

test:
	npx jest
