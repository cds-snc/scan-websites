module "rds" {
  source = "github.com/cds-snc/terraform-modules?ref=v3.0.16//rds"

  name           = "scan-websites"
  database_name  = "scan_websites"
  instances      = 1
  instance_class = "db.serverless"
  engine         = "aurora-postgresql"
  engine_version = "14.3"
  username       = var.rds_username
  password       = var.rds_password

  vpc_id                      = module.vpc.vpc_id
  subnet_ids                  = module.vpc.private_subnet_ids
  preferred_backup_window     = "07:00-09:00"
  backup_retention_period     = 1
  allow_major_version_upgrade = true
  
  /* 
  When upgrade_immediately is set to TRUE there will be db downtime
  as your db will be taken offline immediately instead of being rebuilt
  in the next maintenance window. 
  
  **TAKE A SNAPSHOT BEFORE APPLYING AND BE READY TO ROLLBACK IF UPGRADE DOES NOT GO SMOOTHLY** 
  */
  upgrade_immediately         = true

  serverless_min_capacity = 0.5
  serverless_max_capacity = 1.0

  billing_tag_value = var.billing_code
}
