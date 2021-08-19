output "owasp_zap_report_data_bucket_id" {
  value = module.owasp_zap_report_data.s3_bucket_id
}

output "owasp_zap_urls_topic_arn" {
  value = aws_sns_topic.owasp-zap-urls.arn
}