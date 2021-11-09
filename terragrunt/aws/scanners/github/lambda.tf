module "github_scanner" {
  name              = "scanners-github"
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.39//lambda"
  image_uri         = "${aws_ecr_repository.scanners-github.repository_url}:latest"
  billing_tag_value = var.billing_tag

  environment_variables = {
    "REPORT_DATA_BUCKET" = var.github_report_data_bucket_id
    "SCREENSHOT_BUCKET"  = var.github_screenshots_bucket_id
  }

  policies = [data.aws_iam_policy_document.api_policies.json]
  sns_topic_arns = [
    var.github_urls_topic_arn
  ]
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
      aws_ecr_repository.scanners-github.arn
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
