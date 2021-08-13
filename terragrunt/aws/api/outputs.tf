output "axe_core_report_data_bucket_id" {
  value = aws_s3_bucket.axe-core-report-data.id
}

output "axe_core_screenshots_bucket_id" {
  value = aws_s3_bucket.axe-core-screenshots.id
}

output "axe_core_urls_topic_arn" {
  value = aws_sns_topic.axe-core-urls.arn
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