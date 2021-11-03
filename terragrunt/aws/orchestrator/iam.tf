data "aws_iam_policy_document" "service_principal" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    principals {
      type        = "Service"
      identifiers = ["ecs.amazonaws.com"]
    }

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    principals {
      type        = "Service"
      identifiers = ["states.${var.region}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "orchestrator" {
  name               = "${var.product_name}-orchestrator"
  assume_role_policy = data.aws_iam_policy_document.service_principal.json
}

data "aws_iam_policy" "lambda_insights" {
  name = "CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "lambda_insights" {
  role       = aws_iam_role.orchestrator.name
  policy_arn = data.aws_iam_policy.lambda_insights.arn
}

data "aws_iam_policy_document" "scan_runner_policies" {

  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      aws_cloudwatch_log_group.owasp-zap-log.arn,
      "${aws_cloudwatch_log_group.owasp-zap-log.arn}:log-group:${aws_cloudwatch_log_group.owasp-zap-log.name}:log-stream:*",
      aws_cloudwatch_log_group.nuclei-log.arn,
      "${aws_cloudwatch_log_group.nuclei-log.arn}:log-group:${aws_cloudwatch_log_group.nuclei-log.name}:log-stream:*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecr:GetDownloadUrlForlayer",
      "ecr:BatchGetImage"
    ]
    resources = [
      aws_ecr_repository.orchestrator.arn,
      aws_ecr_repository.runners-owasp-zap.arn,
      aws_ecr_repository.runners-nuclei.arn,
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:RunTask"
    ]

    resources = [
      aws_ecs_task_definition.runners-nuclei.arn,
      aws_ecs_task_definition.runners-owasp-zap.arn
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "states:ListStateMachines",
      "states:ListActivities",
      "states:CreateStateMachine",
      "states:CreateActivity",
      "states:DescribeExecution",
      "states:StartExecution",
      "states:StopExecution"
    ]

    resources = [
      "arn:aws:states:${var.region}:${var.account_id}:*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule"
    ]

    resources = [
      "arn:aws:events:${var.region}:${var.account_id}:*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      aws_iam_role.container_execution_role.arn,
      aws_iam_role.orchestrator.arn,
      aws_iam_role.task_execution_role.arn
    ]
  }

}

resource "aws_iam_policy" "orchestrator" {
  name   = "${var.product_name}-orchestrator"
  path   = "/"
  policy = data.aws_iam_policy_document.scan_runner_policies.json
}

resource "aws_iam_role_policy_attachment" "scan_runner" {
  role       = aws_iam_role.orchestrator.name
  policy_arn = aws_iam_policy.orchestrator.arn
}

# Use AWS managed IAM policy
####
# Provides minimum permissions for a Lambda function to execute while
# accessing a resource within a VPC - create, describe, delete network
# interfaces and write permissions to CloudWatch Logs.
####
resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.orchestrator.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
