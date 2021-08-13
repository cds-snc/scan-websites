.PHONY: apply fmt
apply:
  terragrunt apply --terragrunt-non-interactive -auto-approve

fmt:
  terragrunt hclfmt