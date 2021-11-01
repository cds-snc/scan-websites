###
# Container Execution Role
###
# Role that the Amazon ECS container agent and the Docker daemon can assume
###

resource "aws_iam_role" "container_execution_role_sqm" {
  name               = "scan_queue_manager_container_execution_role"
  assume_role_policy = data.aws_iam_policy_document.container_execution_role_sqm.json
}

resource "aws_iam_role_policy_attachment" "ce_cs_sqm" {
  role       = aws_iam_role.container_execution_role_sqm.name
  policy_arn = data.aws_iam_policy.ec2_container_service.arn
}

resource "aws_iam_role_policy_attachment" "ce_sfn_sqm" {
  role       = aws_iam_role.container_execution_role_sqm.name
  policy_arn = aws_iam_policy.scanners-scan-queue-manager.arn
}


###
# Policy Documents
###

data "aws_iam_policy_document" "container_execution_role_sqm" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    principals {
      type        = "Service"
      identifiers = ["states.${var.region}.amazonaws.com"]
    }
  }

  
  
}

data "aws_iam_policy" "ec2_container_service" {
  name = "AmazonEC2ContainerServiceforEC2Role"
}