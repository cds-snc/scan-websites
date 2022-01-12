terraform {
  source = "../../aws//tf_roles"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  account_id = var.account_id
}