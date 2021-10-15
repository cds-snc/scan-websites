#
# Lambda: post notifications to Slack
#
module "notify_slack" {
  source = "github.com/cds-snc/terraform-modules?ref=v0.0.36//notify_slack"

  function_name     = "notify_slack"
  project_name      = "Scan Websites"
  slack_webhook_url = var.slack_webhook_url

  sns_topic_arns = [
    var.sns_topic_warning_arn,
    var.sns_topic_critical_arn
  ]

  billing_tag_key   = "CostCenter"
  billing_tag_value = var.billing_code
}

resource "aws_sns_topic_subscription" "warning" {
  topic_arn = var.sns_topic_warning_arn
  protocol  = "lambda"
  endpoint  = module.notify_slack.lambda_arn
}

resource "aws_sns_topic_subscription" "critical" {
  topic_arn = var.sns_topic_critical_arn
  protocol  = "lambda"
  endpoint  = module.notify_slack.lambda_arn
}
