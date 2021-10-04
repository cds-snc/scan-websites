resource "aws_ecr_repository" "scanners-owasp-zap" {
  name                 = "${var.product_name}/scanners/owasp-zap"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "runners-owasp-zap" {
  name                 = "${var.product_name}/runners/owasp-zap"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}