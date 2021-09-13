resource "aws_route53_zone" "scan_websites" {
  name = var.hosted_zone_name

  tags = {
    CostCenter = var.billing_code
  }
}