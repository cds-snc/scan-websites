terraform {
  source = "../../aws//api"
}


inputs = {
  rds_username = "databaseuser"
}

include {
  path = find_in_parent_folders()
}
