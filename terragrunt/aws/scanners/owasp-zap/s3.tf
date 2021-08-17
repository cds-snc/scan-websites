locals {
  owasp_zap_report_data_name = "${var.product_name}-${var.env}-owasp-zap-report-data"
}

module "owasp-zap-report-data" {
  source = "github.com/cds-snc/terraform-modules?ref=0.0.28//S3"
  bucket_name = local.owasp_zap_report_data_name

  versioning = {
    enabled = true
  }

  logging = {
    target_bucket = var.log_bucket_id
    target_prefix = local.owasp_zap_report_data_name
  }

  billing_tag_value = var.product_name
}

