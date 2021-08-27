.PHONY: build test fmt lint install-dev install fmt-ci lint-ci

build:

test:

fmt-ci: fmt

fmt:
	terraform fmt -recursive aws && \
	terragrunt hclfmt

build:

install:

install-dev:
	pip3 install --upgrade requests setuptools && \
	pip3 install --upgrade botocore checkov

lint-ci: lint

lint:
	checkov --directory=aws

test:
