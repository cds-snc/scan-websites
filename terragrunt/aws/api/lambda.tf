resource "aws_lambda_function" "api" {
  function_name = "api"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.api.repository_url}:latest"

  timeout = 900

  memory_size = 512

  environment {
    variables = {
      CONNECTION_STRING = module.rds.proxy_connection_string_value
    }
  }

  role = aws_iam_role.api.arn

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }
}

resource "aws_lambda_permission" "api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}