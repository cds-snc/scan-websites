resource "aws_cloudwatch_metric_alarm" "lambda_concurrent_executions" {
  alarm_name          = "LambdaConcurrentExecutions"
  alarm_description   = "Average number of concurrent Lambda invocations in a 1 minute period."
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Average"
  threshold           = var.lambda_concurrent_executions
  treat_missing_data  = "notBreaching"

  alarm_actions = [var.sns_topic_warning_arn]
  ok_actions    = [var.sns_topic_warning_arn]
}
