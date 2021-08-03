module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.11//vpc"
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

resource "aws_security_group" "api_lambda" {
  description = "Security group that is to be attached to the api lambda"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "api_lambda_sec_group"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "api_to_rds" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.api_lambda.id
  source_security_group_id = aws_security_group.rds.id
}