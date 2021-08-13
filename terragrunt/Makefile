.PHONY: fmt lint
fmt:
	terraform fmt -recursive .

lint:
	checkov --directory=aws
