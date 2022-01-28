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

resource "aws_iam_role" "api" {
  name               = "${var.product_name}-api"
  assume_role_policy = data.aws_iam_policy_document.service_principal.json
}

data "aws_iam_policy" "lambda_insights" {
  name = "CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "lambda_insights" {
  role       = aws_iam_role.api.name
  policy_arn = data.aws_iam_policy.lambda_insights.arn
}

resource "aws_iam_role_policy_attachment" "lambda_xray_write" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
}

data "aws_iam_policy_document" "api_policies" {

  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "*"
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "ecr:GetDownloadUrlForlayer",
      "ecr:BatchGetImage"
    ]
    resources = [
      aws_ecr_repository.api.arn
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "sns:Publish"
    ]
    resources = [
      aws_sns_topic.axe-core-urls.arn,
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "states:ListStateMachines",
      "states:ListActivities",
      "states:CreateActivity",
      "states:DescribeExecution",
      "states:StartExecution",
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
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]

    resources = [aws_kms_key.scan-websites.arn]
  }

  statement {

    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:GetBucketLocation",
      "s3:Get*",
      "s3:Put*"
    ]
    resources = [
      module.owasp-zap-report-data.s3_bucket_arn,
      "${module.owasp-zap-report-data.s3_bucket_arn}/*",
      module.axe-core-report-data.s3_bucket_arn,
      "${module.axe-core-report-data.s3_bucket_arn}/*",
      module.axe-core-screenshots.s3_bucket_arn,
      "${module.axe-core-screenshots.s3_bucket_arn}/*",
      module.github-report-data.s3_bucket_arn,
      "${module.github-report-data.s3_bucket_arn}/*",
      module.nuclei-report-data.s3_bucket_arn,
      "${module.nuclei-report-data.s3_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_policy" "api" {
  name   = "${var.product_name}-api"
  path   = "/"
  policy = data.aws_iam_policy_document.api_policies.json
}

resource "aws_iam_role_policy_attachment" "api" {
  role       = aws_iam_role.api.name
  policy_arn = aws_iam_policy.api.arn
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

## WAF log IAM role

resource "aws_iam_role" "waf_log_role" {
  name               = "${var.product_name}-logs"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume_role.json

  tags = {
    CostCentre = var.billing_code
    Terraform  = true
  }
}

resource "aws_iam_policy" "write_waf_logs" {
  name        = "${var.product_name}_WriteLogs"
  description = "Allow writing WAF logs to S3 + CloudWatch"
  policy      = data.aws_iam_policy_document.write_waf_logs.json

  tags = {
    CostCentre = var.billing_code
    Terraform  = true
  }
}

resource "aws_iam_role_policy_attachment" "write_waf_logs" {
  role       = aws_iam_role.waf_log_role.name
  policy_arn = aws_iam_policy.write_waf_logs.arn
}

data "aws_iam_policy_document" "firehose_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "write_waf_logs" {
  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      "arn:aws:s3:::${var.cbs_satellite_bucket_name}"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject*",
      "s3:PutObject*",
    ]

    resources = [
      "arn:aws:s3:::${var.cbs_satellite_bucket_name}/waf_logs/*"
    ]
  }
}