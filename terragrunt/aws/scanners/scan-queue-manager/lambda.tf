resource "aws_lambda_function" "scanners-scan-queue-manager" {
  function_name = "scanners-scan-queue-manager"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-scan-queue-manager.repository_url}:latest"

  role    = aws_iam_role.scanners-scan-queue-manager.arn
  timeout = 60

  memory_size = 1024

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      REPORT_DATA_BUCKET = var.owasp_zap_report_data_bucket_id
      CLUSTER            = var.scanning_tools_cluster_arn
      TASK_DEF_ARN       = ""
      STEP_FUNC_ROLE_ARN = aws_iam_role.container_execution_role_sqm.arn
      PRIVATE_SUBNETS    = join(",", var.private_subnet_ids)
      SECURITY_GROUP     = aws_security_group.scanning_tools_web_scanning.id
      SCAN_THREADS       = var.scan_threads
      MIN_ECS_CAPACITY   = var.min_ecs_capacity
      MAX_ECS_CAPACITY   = var.max_ecs_capacity
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.scanning_tools_web_scanning.id]
    subnet_ids         = var.private_subnet_ids
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_cloudwatch_log_group" "log" {
  name              = "/aws/lambda/scanners-scan-queue-manager"
  retention_in_days = 14
}