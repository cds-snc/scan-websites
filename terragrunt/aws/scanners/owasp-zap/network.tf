resource "aws_security_group" "security_tools_web_scanning" {
  name        = "web-security-scanners-sg "
  description = "Web access for Security Scanners"
  vpc_id      = var.vpc_id

  tags = {
    CostCenter = var.product_name
  }
}

resource "aws_security_group_rule" "web_port_80_egress" {
  description       = "Security group rule for egress to port 80"
  type              = "egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.security_tools_web_scanning.id
}

resource "aws_security_group_rule" "web_port_443_egress" {
  description       = "Security group rule for egress to port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.security_tools_web_scanning.id
}