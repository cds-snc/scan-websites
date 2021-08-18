resource "aws_s3_bucket" "owasp-zap-report-data" {
  bucket = "${var.product_name}-owasp-zap-report-data"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  tags = {
    CostCenter = var.product_name
  }
}

resource "aws_s3_bucket_public_access_block" "owasp-zap-report-data" {
  bucket = aws_s3_bucket.owasp-zap-report-data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
