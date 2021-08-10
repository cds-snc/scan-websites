resource "aws_s3_bucket" "axe-core-report-data" {
  bucket = "${var.product_name}-${var.env}-axe-core-report-data"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    CostCenter = var.billing_code
  }
}
