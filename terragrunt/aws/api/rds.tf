module "rds" {
  source                  = "github.com/cds-snc/terraform-modules?ref=v0.0.27//rds"
  backup_retention_period = 1
  billing_tag_value       = var.billing_code
  database_name           = "scan_websites"
  instances               = 1
  name                    = "scan-websites"
  preferred_backup_window = "07:00-09:00"
  subnet_ids              = module.vpc.private_subnet_ids
  username                = var.rds_username
  password                = var.rds_password
  vpc_id                  = module.vpc.vpc_id
  engine_version          = "13.6"
}
