resource "aws_ecr_repository" "scanners-axe-core" {
  name                 = "${var.product_name}/scanners/axe-core"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}