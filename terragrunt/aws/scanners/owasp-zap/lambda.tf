resource "aws_lambda_function" "scanners-owasp-zap" {
  # checkov:skip=CKV_AWS_50:X-ray tracing only required during function debug
  # checkov:skip=CKV_AWS_115:Reserved concurrency not required (not latency sensitive)
  function_name = "scanners-owasp-zap"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-owasp-zap.repository_url}:latest"

  role    = aws_iam_role.scanners-owasp-zap.arn
  timeout = 60

  memory_size = 1024

  environment {
    variables = {
      REPORT_DATA_BUCKET     = module.owasp_zap_report_data.s3_bucket_id
      CLUSTER                = aws_ecs_cluster.scanning_tools.arn
      TASK_DEF_ARN           = aws_ecs_task_definition.runners-owasp-zap.arn
      PRIVATE_SUBNETS        = join(",", var.private_subnet_ids)
      SECURITY_GROUP         = aws_security_group.security_tools_web_scanning.id
      DOMAIN                 = "https://${var.domain_name}"
      PRIVATE_API_AUTH_TOKEN = var.private_api_auth_token
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.security_tools_web_scanning.id]
    subnet_ids         = var.private_subnet_ids
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_sns_topic_subscription" "scanners-owasp-zap-lambda-subscription" {
  topic_arn = aws_sns_topic.owasp-zap-urls.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.scanners-owasp-zap.arn
}

resource "aws_lambda_permission" "scanners-owasp-zap" {
  statement_id  = "AllowZapRunnerSNSInvoke"
  function_name = aws_lambda_function.scanners-owasp-zap.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.owasp-zap-urls.arn
}
