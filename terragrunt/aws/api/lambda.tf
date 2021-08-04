resource "aws_lambda_function" "api" {
  function_name = "api"

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.api.repository_url}:latest"

  role = aws_iam_role.api.arn
  timeout = 60

  memory_size = 1024

  environment {
    variables = {
      SQLALCHEMY_DATABASE_URI = module.rds.proxy_connection_string_value
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.api_lambda.id]
    subnet_ids = module.vps.subnet_ids
  }

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

resource "aws_iam_role" "api" {
  name               = "api_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.service_principal_api.json
}

data "aws_iam_policy_document" "service_principal_api" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


# Use AWS managed IAM policy
####
# Provides minimum permissions for a Lambda function to execute while 
# accessing a resource within a VPC - create, describe, delete network 
# interfaces and write permissions to CloudWatch Logs.
####
resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}