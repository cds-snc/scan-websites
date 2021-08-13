resource "aws_ecr_repository" "scanners-owasp-zap" {
  # checkov:skip=CKV_AWS_51:The :latest tag is used in Staging

  name                 = "${var.product_name}/scanners/owasp-zap"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }
}