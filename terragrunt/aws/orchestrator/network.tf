resource "aws_security_group" "security_tools_scanning" {
  name        = "security-scanners-sg"
  description = "Internet access for Security Scanners"
  vpc_id      = var.vpc_id

  tags = {
    CostCenter = var.product_name
  }
}

resource "aws_security_group_rule" "all_egress" {
  description       = "Security group rule for egress to all ports and protocols"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.security_tools_scanning.id
}