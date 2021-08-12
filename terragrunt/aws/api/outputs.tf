output "axe_core_report_data_bucket_id" {
  value = aws_s3_bucket.axe-core-report-data.id
}

output "axe_core_screenshots_bucket_id" {
  value = aws_s3_bucket.axe-core-screenshots.id
}

output "axe_core_urls_topic_arn" {
  value = aws_sns_topic.axe-core-urls.arn
}
