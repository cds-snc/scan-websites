terraform {
  source = "../../../aws//scanners/axe-core"
}

dependencies {
  paths = ["../../api"]
}

dependency "api" {
  config_path = "../../api"

  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
  mock_outputs = {
    axe_core_report_data_bucket_id = ""
    axe_core_screenshots_bucket_id = ""
    axe_core_urls_topic_arn        = ""
  }
}

inputs = {
  axe_core_report_data_bucket_id = dependency.api.outputs.axe_core_report_data_bucket_id
  axe_core_screenshots_bucket_id = dependency.api.outputs.axe_core_screenshots_bucket_id
  axe_core_urls_topic_arn        = dependency.api.outputs.axe_core_urls_topic_arn
}

include {
  path = find_in_parent_folders()
}
