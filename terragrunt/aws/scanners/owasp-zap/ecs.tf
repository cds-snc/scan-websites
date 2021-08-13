resource "aws_ecs_cluster" "scanning_tools" {
  name = "scanning-tools"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

}

resource "aws_ecs_task_definition" "zap_runner" {
  family       = "zap_runner"
  cpu          = 2048
  memory       = 16384
  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.container_execution_role.arn
  task_role_arn            = aws_iam_role.task_execution_role.arn
  container_definitions    = data.template_file.scanning_tools.rendered

  tags = {
    CostCentre = var.billing_code
  }
}

resource "aws_cloudwatch_log_group" "log" {
  # checkov:skip=CKV_AWS_158:Encryption using default CloudWatch service key is acceptable
  name              = "/aws/ecs/zap_runner_ecs"
  retention_in_days = 14
}

data "template_file" "scanning_tools" {
  template = file("container-definitions/zap_runner.json")
  vars = {
    image                 = "${aws_ecr_repository.scanners-owasp-zap.repository_url}:latest"
    awslogs-region        = "ca-central-1"
    awslogs-stream-prefix = "ecs-zap-runner"
    s3_name               = aws_s3_bucket.owasp-zap-report-data.bucket
    awslogs-group         = aws_cloudwatch_log_group.log.name
    name                  = "zap_runner"
  }
}

