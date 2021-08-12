module "ops_alarms" {
  source                = "github.com/cds-snc/terraform-modules?ref=v0.0.21//user_login_alarm"
  account_names         = ["ops1", "ops2"]
  namespace             = "ops_alarms"
  log_group_name        = "CloudTrail/Landing-Zone-Logs"
  alarm_actions_success = [aws_sns_topic.critical.arn]
  alarm_actions_failure = [aws_sns_topic.warning.arn]
  num_attempts          = 1
}

