locals {
  owasp_zap_report_data_name = "${var.product_name}-${var.env}-owasp-zap-report-data"
}


module "owasp_zap_report_data" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.owasp_zap_report_data_name
  versioning = {
    enabled = true
  }
  billing_tag_value = var.billing_code
  logging = {
    "target_bucket" = var.log_bucket_id
    "target_prefix" = local.owasp_zap_report_data_name
  }
}
