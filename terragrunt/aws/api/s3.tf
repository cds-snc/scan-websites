locals = {
  name_prefix = "${var.product_name}-${var.env}"
  axe_core_report_data_name = "${local.name_prefix}-axe-core-report-data"
  axe_core_screenshots_name = "${local.name_prefix}-axe-core-screenshots"
}

module "axe-core-report-data" {
  source = "github.com/cds-snc/terraform-modules?ref=0.0.28//S3"
  bucket_name = local.axe_core_report_data_name
  lifecycle_rule = {
    "id" = "expire"
    "enabled" = true
    "expiration" = {
      "days" = 30
    }
  }
  billing_tag_value = var.billing_code 
  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.axe_core_report_data_name
  }
}

module "axe-core-screenshots" {
  source = "github.com/cds-snc/terraform-modules?ref=0.0.28//S3"
  bucket_name = local.axe_core_screenshots_name
  lifecycle_rule = {
    "id" = "expire"
    "enabled" = true
    "expiration" = {
      "days" = 30
    }
  }
  billing_tag_value = var.billing_code 

  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.axe_core_screenshots_name
  }
}

module "log_bucket" {
  source = "github.com/cds-snc/terraform-modules?ref=0.0.28//S3_log_bucket"
  bucket_name = "${var.product_name}-${var.env}-logs"
  billing_tag_value = var.billing_code 

}