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
  }
}

inputs = {
  vpc_id                    = dependency.api.outputs.vpc_id
  private_subnet_ids        = dependency.api.outputs.private_subnet_ids
  scan_websites_kms_key_arn = dependency.api.outputs.scan_websites_kms_key_arn
}

include {
  path = find_in_parent_folders()
}
