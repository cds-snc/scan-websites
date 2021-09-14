terraform {
  source = "../../../aws//scanners/owasp-zap"
}

dependencies {
  paths = ["../../api"]
}

dependency "api" {
  config_path = "../../api"

  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
  mock_outputs = {
    vpc_id                    = ""
    private_subnet_ids        = ""
    scan_websites_kms_key_arn = ""
    domain_name               = "example.com"
  }
}

inputs = {
  vpc_id                    = dependency.api.outputs.vpc_id
  private_subnet_ids        = dependency.api.outputs.private_subnet_ids
  scan_websites_kms_key_arn = dependency.api.outputs.scan_websites_kms_key_arn
  log_bucket_id             = dependency.api.outputs.log_bucket_id
  domain_name               = dependency.api.outputs.domain_name
}

include {
  path = find_in_parent_folders()
}
