resource "aws_sns_topic" "owasp-zap-urls" {
  name              = "owasp-zap-urls"
  kms_master_key_id = var.scan_websites_kms_key_arn

  tags = {
    CostCenter = var.product_name
  }
}
