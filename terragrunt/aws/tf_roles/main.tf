module "plan_role" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.48//gh_oicd_role"
  role_name         = "gh_plan_role"
  repo              = "scan-websites"
  billing_tag_value = var.billing_code
}

data "aws_iam_policy" "readonly" {
  name = "ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "readonly" {
  role       = module.plan_role.role_name
  policy_arn = data.aws_iam_policy.readonly.arn
}

module "apply_role" {
  source            = "github.com/cds-snc/terraform-modules?ref=v0.0.48//gh_oicd_role"
  role_name         = "gh_plan_role"
  repo              = "scan-websites"
  claim             = "ref:refs/heads/main"
  billing_tag_value = var.billing_code
}

data "aws_iam_policy" "admin" {
  name = "AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = module.apply_role.role_name
  policy_arn = data.aws_iam_policy.admin.arn
}