module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.21//vpc"
  name              = var.product_name
  billing_tag_value = var.billing_code
  high_availability = true
  enable_flow_log   = false
}