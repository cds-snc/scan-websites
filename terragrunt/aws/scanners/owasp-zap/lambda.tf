resource "aws_lambda_function" "scanners-owasp-zap" {
  function_name = "scanners-owasp-zap"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-owasp-zap.repository_url}:latest"

  role    = aws_iam_role.scanners-owasp-zap.arn
  timeout = 60

  memory_size = 1024

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      REPORT_DATA_BUCKET = var.owasp_zap_report_data_bucket_id
      CLUSTER            = var.scanning_tools_cluster_arn
      TASK_DEF_ARN       = aws_ecs_task_definition.runners-owasp-zap.arn
      PRIVATE_SUBNETS    = join(",", var.private_subnet_ids)
      SECURITY_GROUP     = aws_security_group.security_tools_web_scanning.id
      SCAN_THREADS       = var.owasp_zap_scan_threads
      MIN_ECS_CAPACITY   = var.min_ecs_capacity
      MAX_ECS_CAPACITY   = var.max_ecs_capacity
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
  topic_arn = var.owasp_zap_urls_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.scanners-owasp-zap.arn
}

resource "aws_lambda_permission" "scanners-owasp-zap" {
  statement_id  = "AllowZapRunnerSNSInvoke"
  function_name = aws_lambda_function.scanners-owasp-zap.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = var.owasp_zap_urls_topic_arn
}
