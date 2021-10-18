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
    vpc_id             = ""
    private_subnet_ids = ""
  }
}

inputs = {
  vpc_id                           = dependency.api.outputs.vpc_id
  private_subnet_ids               = dependency.api.outputs.private_subnet_ids
  owasp_zap_urls_topic_arn         = dependency.api.outputs.owasp_zap_urls_topic_arn
  owasp_zap_report_data_bucket_arn = dependency.api.outputs.owasp_zap_report_data_bucket_arn
  owasp_zap_report_data_bucket_id  = dependency.api.outputs.owasp_zap_report_data_bucket_id
  owasp_zap_scan_threads           = 3
}

include {
  path = find_in_parent_folders()
}
