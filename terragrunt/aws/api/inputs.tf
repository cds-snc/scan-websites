variable "rds_password" {
  type      = string
  sensitive = true
}

variable "rds_username" {
  type = string
}

variable "fastapi_secret_key" {
  type      = string
  sensitive = true
}

variable "google_client_id" {
  type      = string
  sensitive = true
}

variable "google_client_secret" {
  type      = string
  sensitive = true
}

variable "domain_name" {
  type = string
}

variable "hosted_zone_id" {
  type = string
}