resource "aws_sns_topic" "owasp-zap-urls" {
  name              = "owasp-zap-urls"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    CostCenter = var.product_name
  }
}
