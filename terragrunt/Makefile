.PHONY: fmt
fmt:
	terraform fmt -recursive aws &&\
	terragrunt hclfmt

checkov:
	checkov --directory=aws