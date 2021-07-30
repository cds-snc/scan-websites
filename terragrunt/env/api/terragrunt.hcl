terraform {
  source = "../../aws//api"
}


inputs {
  rds_username = "admin"
}

include {
  path = find_in_parent_folders()
}
