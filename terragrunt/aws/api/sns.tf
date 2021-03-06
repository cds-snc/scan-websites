resource "aws_sns_topic" "axe-core-urls" {
  name              = "axe-core-urls"
  kms_master_key_id = aws_kms_key.scan-websites.arn

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_sns_topic" "github-urls" {
  name              = "github-urls"
  kms_master_key_id = aws_kms_key.scan-websites.arn

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_sns_topic" "critical" {
  name              = "critical-alert-scan"
  kms_master_key_id = aws_kms_key.scan-websites.arn

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_sns_topic" "warning" {
  name              = "warning-alert-scan"
  kms_master_key_id = aws_kms_key.scan-websites.arn

  tags = {
    CostCenter = var.billing_code
  }
}