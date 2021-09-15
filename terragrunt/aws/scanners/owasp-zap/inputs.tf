variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(any)
}

variable "owasp_zap_urls_topic_arn" {
  type = string
}

variable "owasp_zap_report_data_bucket_id" {
  type = string
}

variable "owasp_zap_report_data_bucket_arn" {
  type = string
}

variable "private_api_auth_token" {
  type      = string
  sensitive = true
}