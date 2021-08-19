data "aws_iam_policy_document" "service_principal" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scanners-owasp-zap" {
  name               = "${var.product_name}-scanners-owasp-zap"
  assume_role_policy = data.aws_iam_policy_document.service_principal.json
}

data "aws_iam_policy" "lambda_insights" {
  name = "CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "lambda_insights" {
  role       = aws_iam_role.scanners-owasp-zap.name
  policy_arn = data.aws_iam_policy.lambda_insights.arn
}

data "aws_iam_policy_document" "zap_runner_policies" {

  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      aws_cloudwatch_log_group.log.arn,
      "${aws_cloudwatch_log_group.log.arn}:log-group:${aws_cloudwatch_log_group.log.name}:log-stream:*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecr:GetDownloadUrlForlayer",
      "ecr:BatchGetImage"
    ]
    resources = [
      aws_ecr_repository.scanners-owasp-zap.arn
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:RunTask"
    ]

    resources = [
      aws_ecs_task_definition.runners-owasp-zap.arn
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      aws_iam_role.container_execution_role.arn,
      aws_iam_role.task_execution_role.arn
    ]
  }

}

resource "aws_iam_policy" "scanners-owasp-zap" {
  name   = "${var.product_name}-scanners-owasp-zap"
  path   = "/"
  policy = data.aws_iam_policy_document.zap_runner_policies.json
}

resource "aws_iam_role_policy_attachment" "zap_runner" {
  role       = aws_iam_role.scanners-owasp-zap.name
  policy_arn = aws_iam_policy.scanners-owasp-zap.arn
}

# Use AWS managed IAM policy
####
# Provides minimum permissions for a Lambda function to execute while
# accessing a resource within a VPC - create, describe, delete network
# interfaces and write permissions to CloudWatch Logs.
####
resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.scanners-owasp-zap.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
