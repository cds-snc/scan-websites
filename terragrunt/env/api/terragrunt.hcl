terraform {
  source = "../../aws//api"
}

dependencies {
  paths = ["../hosted_zone"]
}

dependency "hosted_zone" {
  config_path = "../hosted_zone"

  mock_outputs_allowed_terraform_commands = ["init", "fmt", "validate", "plan", "show"]
  mock_outputs = {
    hosted_zone_id = ""
  }
}

inputs = {
  rds_username   = "databaseuser"
  hosted_zone_id = dependency.hosted_zone.outputs.hosted_zone_id
  domain_name    = "scan-websites.alpha.canada.ca"
}

include {
  path = find_in_parent_folders()
}
