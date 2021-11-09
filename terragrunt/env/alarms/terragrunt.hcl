terraform {
  source = "../../aws//alarms"
}

dependencies {
  paths = ["../api"]
}

dependency "api" {
  config_path = "../api"

  mock_outputs_allowed_terraform_commands = ["init", "fmt", "validate", "plan", "show"]
  mock_outputs = {
    sns_topic_critical_arn = ""
    sns_topic_warning_arn  = ""
  }
}

inputs = {
  lambda_concurrent_executions = 700
  sns_topic_critical_arn       = dependency.api.outputs.sns_topic_critical_arn
  sns_topic_warning_arn        = dependency.api.outputs.sns_topic_warning_arn
}

include {
  path = find_in_parent_folders()
}
