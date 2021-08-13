resource "aws_s3_bucket" "axe-core-report-data" {
  bucket = "${var.product_name}-${var.env}-axe-core-report-data"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "expire"
    enabled = true

    expiration {
      days = 30
    }
  }

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_s3_bucket_public_access_block" "axe-core-report-data" {
  bucket = aws_s3_bucket.axe-core-report-data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "axe-core-screenshots" {
  bucket = "${var.product_name}-${var.env}-axe-core-screenshots"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "expire"
    enabled = true

    expiration {
      days = 30
    }
  }

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_s3_bucket_public_access_block" "axe-core-screenshots" {
  bucket = aws_s3_bucket.axe-core-screenshots.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}