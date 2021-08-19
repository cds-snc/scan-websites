data "aws_iam_policy_document" "task_execution_role" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "zap_runner_container_policies" {

  statement {

    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",

    ]
    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "arn:aws:lambda:${var.region}:${var.account_id}:function:${var.product_name}*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      aws_cloudwatch_log_group.log.arn,
      "${aws_cloudwatch_log_group.log.arn}:log-stream:*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface"
    ]

    resources = [
      "arn:aws:ec2:${var.region}:${var.account_id}:network-interface/*"
    ]

  }

  statement {

    effect = "Allow"

    actions = [
      "ec2:DescribeNetworkInterfaces"
    ]

    resources = [
      "*"
    ]

  }

  statement {

    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl",
    ]
    resources = [module.owasp_zap_report_data.s3_bucket_arn]

  }

}
