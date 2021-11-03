resource "aws_ecs_task_definition" "runners-owasp-zap" {
  family       = "runners-owasp-zap"
  cpu          = 2048
  memory       = 16384
  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.container_execution_role.arn
  task_role_arn            = aws_iam_role.task_execution_role.arn
  container_definitions    = data.template_file.runners-owasp-zap.rendered

  tags = {
    CostCentre = var.billing_code
  }
}

resource "aws_cloudwatch_log_group" "owasp-zap-log" {
  name              = "/aws/ecs/runners_owasp_zap_ecs"
  retention_in_days = 14
}

data "template_file" "runners-owasp-zap" {
  template = file("container-definitions/runners-owasp-zap.json")
  vars = {
    image                 = "${aws_ecr_repository.runners-owasp-zap.repository_url}:latest"
    awslogs-region        = "ca-central-1"
    awslogs-stream-prefix = "ecs-runners-owasp-zap"
    s3_name               = var.owasp_zap_report_data_bucket_id
    awslogs-group         = aws_cloudwatch_log_group.owasp-zap-log.name
    name                  = "runners-owasp-zap"
  }
}

resource "aws_ecs_task_definition" "runners-nuclei" {
  family       = "runners-nuclei"
  cpu          = 2048
  memory       = 16384
  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.container_execution_role.arn
  task_role_arn            = aws_iam_role.task_execution_role.arn
  container_definitions    = data.template_file.runners-nuclei.rendered

  tags = {
    CostCentre = var.billing_code
  }
}

resource "aws_cloudwatch_log_group" "nuclei-log" {
  name              = "/aws/ecs/runners_nuclei_ecs"
  retention_in_days = 14
}

data "template_file" "runners-nuclei" {
  template = file("container-definitions/runners-nuclei.json")
  vars = {
    image                 = "${aws_ecr_repository.runners-nuclei.repository_url}:latest"
    awslogs-region        = "ca-central-1"
    awslogs-stream-prefix = "ecs-runners-nuclei"
    s3_name               = var.owasp_zap_report_data_bucket_id
    awslogs-group         = aws_cloudwatch_log_group.nuclei-log.name
    name                  = "runners-nuclei"
  }
}

