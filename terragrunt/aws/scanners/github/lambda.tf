resource "aws_lambda_function" "scanners-github" {
  function_name = "scanners-github"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scanners-github.repository_url}:latest"

  role    = aws_iam_role.scanners-github.arn
  timeout = 60

  memory_size = 1600

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      REPORT_DATA_BUCKET = var.github_report_data_bucket_id
      SCREENSHOT_BUCKET  = var.github_screenshots_bucket_id
    }
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_sns_topic_subscription" "scanners-github-lambda-subscription" {
  topic_arn = var.github_urls_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.scanners-github.arn
}

resource "aws_lambda_permission" "scanners-github-lambda-permission" {
  function_name = aws_lambda_function.scanners-github.function_name
  action        = "lambda:InvokeFunction"
  principal     = "sns.amazonaws.com"
  source_arn    = var.github_urls_topic_arn
}
