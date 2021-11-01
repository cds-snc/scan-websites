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

variable "scanning_tools_cluster_arn" {
  type = string
}

variable "scan_threads" {
  type = number
}

variable "min_ecs_capacity" {
  type = number
}

variable "max_ecs_capacity" {
  type = number
}