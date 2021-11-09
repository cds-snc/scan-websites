variable "lambda_concurrent_executions" {
  description = "Threshold of Lambda concurrent executions before an alarm is triggered"
  type        = number
}

variable "slack_webhook_url" {
  description = "Slack incoming webhook URL to post the alarm notifications to"
  type        = string
  sensitive   = true
}

variable "sns_topic_critical_arn" {
  description = "Critical SNS Topic ARN"
  type        = string
}

variable "sns_topic_warning_arn" {
  description = "Warning SNS Topic ARN"
  type        = string
}
