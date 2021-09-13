module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.21//vpc"
  name              = var.product_name
  billing_tag_value = var.billing_code
  high_availability = true
  enable_flow_log   = false
}

resource "aws_security_group" "api" {

  name        = "${var.product_name}_api_sg"
  description = "SG for the API lambda"

  vpc_id = module.vpc.vpc_id

  tags = {
    CostCentre = var.billing_code
    Name       = "${var.product_name}_api_sg"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
}