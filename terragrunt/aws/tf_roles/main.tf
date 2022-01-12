locals {
  plan_name  = "gh_plan_role"
  admin_name = "gh_admin_role"
}

module "gh_oidc_roles" {
  source = "github.com/cds-snc/terraform-modules?ref=v1.0.0//gh_oidc_role"
  roles = [
    {
      name      = local.plan_name
      repo_name = "scan-websites"
      claim     = "*"
    },
    {
      name      = local.admin_name
      repo_name = "scan-websites"
      claim     = "ref:refs/heads/main"
    }
  ]

  billing_tag_value = var.billing_code
}

data "aws_iam_policy" "readonly" {
  name = "ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "readonly" {
  role       = local.plan_name
  policy_arn = data.aws_iam_policy.readonly.arn
}

module "attach_tf_plan_policy" {
  source            = "github.com/cds-snc/terraform-modules?ref=v1.0.2//attach_tf_plan_policy"
  account_id        = var.account_id
  role_name         = local.plan_name
  bucket_name       = "scan-websites-production-tf"
  billing_tag_value = var.billing_code
}

data "aws_iam_policy" "admin" {
  name = "AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = local.admin_name
  policy_arn = data.aws_iam_policy.admin.arn
}
