terraform {
  source = "../../aws//ecs"
}

include {
  path = find_in_parent_folders()
}
