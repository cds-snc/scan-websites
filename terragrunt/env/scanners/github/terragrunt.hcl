terraform {
  source = "../../../aws//scanners/github"
}

dependencies {
  paths = ["../../api"]
}

dependency "api" {
  config_path = "../../api"

  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
  mock_outputs = {
    github_report_data_bucket_id  = ""
    github_report_data_bucket_arn = ""
    github_urls_topic_arn         = ""
  }
}

inputs = {
  github_report_data_bucket_id  = dependency.api.outputs.github_report_data_bucket_id
  github_report_data_bucket_arn = dependency.api.outputs.github_report_data_bucket_arn
  github_urls_topic_arn         = dependency.api.outputs.github_urls_topic_arn
}

include {
  path = find_in_parent_folders()
}
