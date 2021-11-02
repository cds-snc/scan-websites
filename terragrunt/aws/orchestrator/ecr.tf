resource "aws_ecr_repository" "orchestrator" {
  name                 = "${var.product_name}/orchestrator"
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

resource "aws_ecr_repository" "runners-nuclei" {
  name                 = "${var.product_name}/runners/nuclei"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}