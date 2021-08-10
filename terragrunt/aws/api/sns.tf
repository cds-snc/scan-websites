resource "aws_sns_topic" "axe-core-urls" {
  name              = "axe-core-urls"
  kms_master_key_id = aws_kms_key.scan-websites.arn

  tags = {
    CostCenter = var.billing_code
  }
}