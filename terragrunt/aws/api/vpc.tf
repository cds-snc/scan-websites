module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.5//vpc"
  name              = var.product_name
  billing_tag_value = var.billing_code
  high_availability = true
  enable_flow_log   = false
}


resource "aws_security_group" "rds" {
  description = "Security group that is to be attached to RDS"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "rds_sec_group"
  }

  lifecycle {
    create_before_destroy = true
  }
}