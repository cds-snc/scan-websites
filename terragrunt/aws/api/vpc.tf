module "vpc" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.5//vpc"
  name              = var.product_name
  billing_tag_value = var.cost_center_code
  high_availaiblity = true
  enable_flow_log   = false
}