resource "aws_sns_topic" "callback-handler" {
  name              = "callback-handler"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    CostCenter = var.product_name
  }
}

resource "aws_sns_topic" "zap-scan" {
  name              = "zap-scan"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    CostCenter = var.product_name
  }
}
