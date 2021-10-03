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

resource "aws_iam_role" "scanners-axe-core" {
  name               = "${var.product_name}-scanners-axe-core"
  assume_role_policy = data.aws_iam_policy_document.service_principal.json
}

data "aws_iam_policy" "lambda_insights" {
  name = "CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "lambda_insights" {
  role       = aws_iam_role.scanners-axe-core.name
  policy_arn = data.aws_iam_policy.lambda_insights.arn
}

data "aws_iam_policy_document" "api_policies" {

  statement {
    sid    = "CloudWatchAccess"
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
    sid    = "ECRImageAccess"
    effect = "Allow"

    actions = [
      "ecr:GetDownloadUrlForlayer",
      "ecr:BatchGetImage"
    ]
    resources = [
      aws_ecr_repository.scanners-axe-core.arn
    ]
  }

  statement {
    sid    = "S3BucketAccess"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:GetBucketLocation",
      "s3:Get*",
      "s3:Put*"
    ]
    resources = [
      "*"
    ]
  }

}

resource "aws_iam_policy" "scanners-axe-core" {
  name   = "${var.product_name}-scanners-axe-core"
  path   = "/"
  policy = data.aws_iam_policy_document.api_policies.json
}

resource "aws_iam_role_policy_attachment" "scanners-axe-core" {
  role       = aws_iam_role.scanners-axe-core.name
  policy_arn = aws_iam_policy.scanners-axe-core.arn
}
