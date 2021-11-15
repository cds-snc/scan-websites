resource "aws_ecr_repository" "scanners-github" {
  name                 = "${var.product_name}/scanners/github"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}