module "github_scanner" {
  name              = "scanners-github"
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.43//lambda"
  image_uri         = "${aws_ecr_repository.scanners-github.repository_url}:latest"
  ecr_arn           = aws_ecr_repository.scanners-github.arn
  billing_tag_value = var.billing_code

  environment_variables = {
    "REPORT_DATA_BUCKET" = var.github_report_data_bucket_id
  }

  policies = [data.aws_iam_policy_document.api_policies.json]
  sns_topic_arns = [
    var.github_urls_topic_arn
  ]
}

data "aws_iam_policy_document" "api_policies" {

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
      var.github_report_data_bucket_arn,
      "${var.github_report_data_bucket_arn}/*"
    ]
  }

}
