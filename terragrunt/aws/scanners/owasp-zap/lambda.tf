resource "aws_lambda_function" "scanners-owasp-zap" {
  function_name = "scanners-owasp-zap"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-owasp-zap.repository_url}:latest"

  role    = aws_iam_role.scanners-owasp-zap.arn
  timeout = 60

  memory_size = 1024

  environment {
    variables = {
      REPORT_DATA_BUCKET = aws_s3_bucket.owasp-zap-report-data.bucket
      CLUSTER            = aws_ecs_cluster.scanning_tools.arn
      TASK_DEF_ARN       = aws_ecs_task_definition.zap_runner.arn
      PRIVATE_SUBNETS    = join(",", var.private_subnet_ids)
      SECURITY_GROUP     = aws_security_group.security_tools_web_scanning.id
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

resource "aws_lambda_permission" "scanners-owasp-zap" {
  statement_id  = "AllowZapRunnerSNSInvoke"
  function_name = aws_lambda_function.scanners-owasp-zap.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.zap-scan.arn
}
