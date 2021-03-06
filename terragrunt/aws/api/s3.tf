locals {
  name_prefix                = "${var.product_name}-${var.env}"
  axe_core_report_data_name  = "${local.name_prefix}-axe-core-report-data"
  axe_core_screenshots_name  = "${local.name_prefix}-axe-core-screenshots"
  owasp_zap_report_data_name = "${local.name_prefix}-owasp-zap-report-data"
  github_report_data_name    = "${local.name_prefix}-github-report-data"
  nuclei_report_data_name    = "${local.name_prefix}-nuclei-report-data"
}

module "axe-core-report-data" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.axe_core_report_data_name
  lifecycle_rule = [{
    id      = "expire"
    enabled = true
    expiration = {
      days = 30
    }
  }]
  billing_tag_value = var.billing_code
  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.axe_core_report_data_name
  }
}

module "axe-core-screenshots" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.axe_core_screenshots_name
  lifecycle_rule = [{
    id      = "expire"
    enabled = true
    expiration = {
      days = 30
    }
  }]
  billing_tag_value = var.billing_code

  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.axe_core_screenshots_name
  }
}

module "owasp-zap-report-data" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.owasp_zap_report_data_name
  lifecycle_rule = [{
    id      = "expire"
    enabled = true
    expiration = {
      days = 30
    }
  }]
  billing_tag_value = var.billing_code
  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.owasp_zap_report_data_name
  }
}

module "github-report-data" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.github_report_data_name
  lifecycle_rule = [{
    id      = "expire"
    enabled = true
    expiration = {
      days = 30
    }
  }]
  billing_tag_value = var.billing_code
  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.github_report_data_name
  }
}

module "nuclei-report-data" {
  source      = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3"
  bucket_name = local.nuclei_report_data_name
  lifecycle_rule = [{
    id      = "expire"
    enabled = true
    expiration = {
      days = 30
    }
  }]
  billing_tag_value = var.billing_code
  logging = {
    "target_bucket" = module.log_bucket.s3_bucket_id
    "target_prefix" = local.nuclei_report_data_name
  }
}

module "log_bucket" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.28//S3_log_bucket"
  bucket_name       = "${var.product_name}-${var.env}-logs"
  billing_tag_value = var.billing_code

}
