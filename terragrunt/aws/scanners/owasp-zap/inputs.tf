variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(any)
}

variable "scan_websites_kms_key_arn" {
  type = string
}
