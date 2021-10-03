resource "aws_lambda_function" "scanners-axe-core" {
  function_name = "scanners-axe-core"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-axe-core.repository_url}:latest"

  role    = aws_iam_role.scanners-axe-core.arn
  timeout = 60

  memory_size = 1600

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      REPORT_DATA_BUCKET = var.axe_core_report_data_bucket_id
      SCREENSHOT_BUCKET  = var.axe_core_screenshots_bucket_id
    }
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_sns_topic_subscription" "scanners-axe-core-lambda-subscription" {
  topic_arn = var.axe_core_urls_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.scanners-axe-core.arn
}

resource "aws_lambda_permission" "scanners-axe-core-lambda-permission" {
  function_name = aws_lambda_function.scanners-axe-core.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = var.axe_core_urls_topic_arn
}
