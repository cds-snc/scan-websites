resource "aws_lambda_function" "orchestrator" {
  function_name = "orchestrator"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.orchestrator.repository_url}:latest"

  role    = aws_iam_role.orchestrator.arn
  timeout = 60

  memory_size = 1024

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      STEP_FUNC_ARN = aws_sfn_state_machine.dynamic_security_scans.arn
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.security_tools_scanning.id]
    subnet_ids         = var.private_subnet_ids
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_sns_topic_subscription" "orchestrator-lambda-subscription" {
  topic_arn = var.owasp_zap_urls_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.orchestrator.arn
}

resource "aws_lambda_permission" "orchestrator" {
  statement_id  = "AllowZapRunnerSNSInvoke"
  function_name = aws_lambda_function.orchestrator.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = var.owasp_zap_urls_topic_arn
}