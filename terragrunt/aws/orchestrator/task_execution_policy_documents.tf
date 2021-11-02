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
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface"
    ]

    resources = [
      "arn:aws:ec2:${var.region}:${var.account_id}:network-interface/*",
      "arn:aws:ec2:${var.region}:${var.account_id}:subnet/*"
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
    resources = [
      var.owasp_zap_report_data_bucket_arn,
      "${var.owasp_zap_report_data_bucket_arn}/*"
    ]

  }

}
