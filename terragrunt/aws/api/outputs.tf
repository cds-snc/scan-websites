output "axe_core_report_data_bucket_id" {
  value = module.axe-core-report-data.s3_bucket_id
}

output "axe_core_screenshots_bucket_id" {
  value = module.axe-core-screenshots.s3_bucket_id
}

output "axe_core_urls_topic_arn" {
  value = aws_sns_topic.axe-core-urls.arn
}

output "owasp_zap_report_data_bucket_id" {
  value = module.owasp-zap-report-data.s3_bucket_id
}

output "owasp_zap_report_data_bucket_arn" {
  value = module.owasp-zap-report-data.s3_bucket_arn
}

output "owasp_zap_urls_topic_arn" {
  value = aws_sns_topic.owasp-zap-urls.arn
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "scan_websites_kms_key_arn" {
  value = aws_kms_key.scan-websites.arn
}

output "log_bucket_id" {
  value = module.log_bucket.s3_bucket_id
}

output "domain_name" {
  value = aws_api_gateway_domain_name.api.domain_name
}

output "sns_topic_critical_arn" {
  value = aws_sns_topic.critical.arn
}

output "sns_topic_warning_arn" {
  value = aws_sns_topic.warning.arn
}
