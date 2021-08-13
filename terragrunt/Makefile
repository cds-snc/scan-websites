TERRAGRUNT_VERSION="0.31.1"
TERRAGRUNT_CHECKSUM="76b253919ad688025a4a37338e5602543b0426cae1be1f863b4f3d60dd95ac28"

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
	pip3 install --upgrade botocore checkov && \
	echo curl -Lo terragrunt "https://github.com/gruntwork-io/terragrunt/releases/download/v$(TERRAGRUNT_VERSION)/terragrunt_linux_$(dpkg --print-architecture)" && \
    echo "$(TERRAGRUNT_CHECKSUM) terragrunt" | sha256sum --check && \
    chmod +x terragrunt && \
    mv terragrunt /usr/local/bin/

lint-ci: lint

lint:
	checkov --directory=aws

test:
