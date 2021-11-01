resource "aws_security_group" "scanning_tools_web_scanning" {
  name        = "web-security-scanners-all_outbound_sg"
  description = "Web access for Security Scanners"
  vpc_id      = var.vpc_id

  tags = {
    CostCenter = var.product_name
  }
}

resource "aws_security_group_rule" "web_port_all_egress" {
  description       = "Security group rule for egress to port 80"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.scanning_tools_web_scanning.id
}