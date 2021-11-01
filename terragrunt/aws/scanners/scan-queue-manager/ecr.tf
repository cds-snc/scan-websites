resource "aws_ecr_repository" "scanners-scan-queue-manager" {
  name                 = "${var.product_name}/scanners/scan-queue-manager"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}