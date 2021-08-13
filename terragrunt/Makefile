.PHONY: fmt lint
fmt:
	terraform fmt -recursive .

lint:
	checkov --directory=aws

install-dev:
	pip3 install --upgrade requests setuptools && \
	pip3 install --upgrade botocore checkov
