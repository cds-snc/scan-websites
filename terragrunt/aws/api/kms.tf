data "aws_iam_policy_document" "kms_policies" {

  statement {

    effect = "Allow"

    actions = [
      "kms:*"
    ]

    resources = [
      "*"
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }
  }
  statement {

    effect = "Allow"

    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]

    resources = [
      "*"
    ]

    principals {
      type        = "Service"
      identifiers = ["logs.${var.region}.amazonaws.com"]
    }
  }

  statement {

    effect = "Allow"

    actions = [
      "kms:Decrypt*",
      "kms:GenerateDataKey*",
    ]

    resources = [
      "*"
    ]

    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
  }

}

resource "aws_kms_key" "scan-websites" {
  description         = "KMS Key"
  enable_key_rotation = true

  policy = data.aws_iam_policy_document.kms_policies.json

  tags = {
    CostCenter = var.billing_code
  }
}

resource "aws_iam_policy" "kms" {
  name   = "${var.product_name}-kms"
  path   = "/"
  policy = data.aws_iam_policy_document.kms_policies.json
}