variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(any)
}

variable "scan_websites_kms_key_arn" {
  type = string
}

variable "log_bucket_id" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "private_api_auth_token" {
  type      = string
  sensitive = true
}