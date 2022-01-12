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

resource "aws_iam_role_policy_attachment" "terragrunt" {
  role       = local.plan_name
  policy_arn = resource.aws_iam_policy.terragrunt.arn
}

data "aws_iam_policy" "admin" {
  name = "AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = local.admin_name
  policy_arn = data.aws_iam_policy.admin.arn
}


resource "aws_iam_policy" "terragrunt" {
  name   = "Terragrunt"
  policy = aws_iam_policy_document.terragrunt.json
}

data "aws_iam_policy_document" "terragrunt" {

  statement {
    sid    = "AllowAllDynamoDBActionsOnAllTerragruntTables"
    effect = "Allow"
    action = ["dynamodb:*"]
    resource = [
      "arn:aws:dynamodb:*:1234567890:table/terraform-state-lock-dynamo"
    ]
  }

  statement {
    sid    = "AllowAllS3ActionsOnTerragruntBuckets"
    effect = "Allow"
    action = ["s3:*"]
    resource = [
      "arn:aws:s3:::scan-websites-production-tf",
      "arn:aws:s3:::scan-websites-production-tf/*"
    ]
  }

}