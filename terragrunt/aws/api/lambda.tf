data "aws_caller_identity" "current" {}

resource "aws_lambda_function" "api" {
  function_name = "api"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.api.repository_url}:latest"

  role    = aws_iam_role.api.arn
  timeout = 60

  memory_size = 1024

  environment {
    variables = {
      DOMAIN_NAME                         = var.domain_name
      AXE_CORE_URLS_TOPIC                 = aws_sns_topic.axe-core-urls.arn
      AXE_CORE_REPORT_DATA_BUCKET         = module.axe-core-report-data.s3_bucket_id
      AXE_CORE_SCREENSHOT_BUCKET          = module.axe-core-screenshots.s3_bucket_id
      OWASP_ZAP_REPORT_DATA_BUCKET        = module.owasp-zap-report-data.s3_bucket_id
      NUCLEI_REPORT_DATA_BUCKET           = module.nuclei-report-data.s3_bucket_id
      SQLALCHEMY_DATABASE_URI             = module.rds.proxy_connection_string_value
      FASTAPI_SECRET_KEY                  = var.fastapi_secret_key
      GOOGLE_CLIENT_ID                    = var.google_client_id
      GOOGLE_CLIENT_SECRET                = var.google_client_secret
      AWS_LAMBDA_EXEC_WRAPPER             = "/opt/otel-instrument"
      OPENTELEMETRY_COLLECTOR_CONFIG_FILE = "/function/collector.yaml"
      OTEL_BSP_MAX_EXPORT_BATCH_SIZE      = 1
      OTEL_PYTHON_ID_GENERATOR            = "xray"
      OTEL_PROPAGATORS                    = "xray"
      OTEL_EXPORTER_OTLP_ENDPOINT         = "127.0.0.1:4317"
      RERUNING_TASK_ID                    = "0"
    }
  }

  tracing_config {
    mode = "Active"
  }

  vpc_config {
    security_group_ids = [module.rds.proxy_security_group_id, aws_security_group.api.id]
    subnet_ids         = module.vpc.private_subnet_ids
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_lambda_permission" "api" {
  statement_id   = "AllowAPIGatewayInvoke"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.api.function_name
  principal      = "apigateway.amazonaws.com"
  source_arn     = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_lambda_permission" "api-permission-s3" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.api.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = module.axe-core-report-data.s3_bucket_arn
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_s3_bucket_notification" "api-notification" {
  bucket = module.axe-core-report-data.s3_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.api.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.api-permission-s3]
}

resource "aws_lambda_permission" "api-owasp-permission-s3" {
  statement_id   = "AllowExecutionFromOWASPS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.api.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = module.owasp-zap-report-data.s3_bucket_arn
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_s3_bucket_notification" "api-owasp-notification" {
  bucket = module.owasp-zap-report-data.s3_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.api.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.api-owasp-permission-s3]
}

resource "aws_lambda_permission" "api-nuclei-permission-s3" {
  statement_id   = "AllowExecutionFromNucleiS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.api.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = module.nuclei-report-data.s3_bucket_arn
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_s3_bucket_notification" "api-nuclei-notification" {
  bucket = module.nuclei-report-data.s3_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.api.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.api-nuclei-permission-s3]
}
