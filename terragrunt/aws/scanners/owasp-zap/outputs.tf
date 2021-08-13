output "owasp_zap_report_data_bucket_id" {
  value = aws_s3_bucket.owasp-zap-report-data.id
}

output "owasp_zap_urls_topic_arn" {
  value = aws_sns_topic.owasp-zap-urls.arn
}