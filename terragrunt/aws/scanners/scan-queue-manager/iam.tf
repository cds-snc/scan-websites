data "aws_iam_policy_document" "service_principal_sqm" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scanners-scan-queue-manager" {
  name               = "${var.product_name}-scanners-scan-queue-manager"
  assume_role_policy = data.aws_iam_policy_document.service_principal_sqm.json
}

data "aws_iam_policy" "lambda_insights" {
  name = "CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "lambda_insights" {
  role       = aws_iam_role.scanners-scan-queue-manager.name
  policy_arn = data.aws_iam_policy.lambda_insights.arn
}

data "aws_iam_policy_document" "scan_queue_manager_policies" {

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
      "*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:RunTask",
      "states:ListStateMachines",
      "states:ListActivities",
      "states:CreateStateMachine",
      "states:CreateActivity"
    ]

    resources = [
      "*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      aws_iam_role.container_execution_role_sqm.arn,
      aws_iam_role.task_execution_role_sqm.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule",
      "states:DescribeExecution",
      "states:StopExecution"
    ]

    resources = [
      "*"
    ]
  }

}

resource "aws_iam_policy" "scanners-scan-queue-manager" {
  name   = "${var.product_name}-scanners-scan-queue-manager"
  path   = "/"
  policy = data.aws_iam_policy_document.scan_queue_manager_policies.json
}

resource "aws_iam_role_policy_attachment" "scan_queue_manager_runner" {
  role       = aws_iam_role.scanners-scan-queue-manager.name
  policy_arn = aws_iam_policy.scanners-scan-queue-manager.arn
}

# Use AWS managed IAM policy
####
# Provides minimum permissions for a Lambda function to execute while
# accessing a resource within a VPC - create, describe, delete network
# interfaces and write permissions to CloudWatch Logs.
####
resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.scanners-scan-queue-manager.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
