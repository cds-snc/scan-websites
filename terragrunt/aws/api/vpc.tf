module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.21//vpc"
  name              = var.product_name
  billing_tag_value = var.billing_code
  high_availability = true
  enable_flow_log   = false
}


resource "aws_security_group" "rds_lambda" {
  description = "Security group that is to be attached to the RDS module and lambda"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "rds_sec_group"
  }

  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    self      = true
  }

  lifecycle {
    create_before_destroy = true
  }
}
