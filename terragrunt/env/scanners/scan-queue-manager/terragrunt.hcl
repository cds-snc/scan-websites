terraform {
  source = "../../../aws//scanners/scan-queue-manager"
}

dependencies {
  paths = ["../../api", "../../ecs"]
}

dependency "api" {
  config_path = "../../api"

  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
  mock_outputs = {
    vpc_id             = ""
    private_subnet_ids = ""
  }
}

dependency "ecs" {
  config_path = "../../ecs"

  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
  mock_outputs = {
    scanning_tools_cluster_arn = ""
  }
}

inputs = {
  vpc_id                           = dependency.api.outputs.vpc_id
  private_subnet_ids               = dependency.api.outputs.private_subnet_ids
  owasp_zap_urls_topic_arn         = dependency.api.outputs.owasp_zap_urls_topic_arn
  owasp_zap_report_data_bucket_arn = dependency.api.outputs.owasp_zap_report_data_bucket_arn
  owasp_zap_report_data_bucket_id  = dependency.api.outputs.owasp_zap_report_data_bucket_id
  scanning_tools_cluster_arn       = dependency.ecs.outputs.scanning_tools_cluster_arn
  scan_threads                     = 3
  min_ecs_capacity                 = 1
  max_ecs_capacity                 = 5
}

include {
  path = find_in_parent_folders()
}
