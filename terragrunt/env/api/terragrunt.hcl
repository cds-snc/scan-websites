terraform {
  source = "../../aws//api"
}

include {
  path = find_in_parent_folders()
}
