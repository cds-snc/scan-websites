resource "aws_sfn_state_machine" "dynamic_security_scans" {
  name     = "dynamic-security-scans"
  role_arn = aws_iam_role.orchestrator.arn

  definition = data.template_file.dynamic-security-scans.rendered

  tags = {
    CostCentre = var.billing_code
  }
}
data "template_file" "dynamic-security-scans" {
  template = file("step-functions/dynamic-security-scans.json")
  vars = {
    nuclei_container_name = aws_ecs_task_definition.runners-nuclei.family
    nuclei_task_def       = aws_ecs_task_definition.runners-nuclei.arn
    nuclei_report_bucket  = var.nuclei_report_data_bucket_id

    owasp_zap_container_name = aws_ecs_task_definition.runners-owasp-zap.family
    owasp_zap_task_def       = aws_ecs_task_definition.runners-owasp-zap.arn
    owasp_zap_report_bucket  = var.owasp_zap_report_data_bucket_id
    owasp_zap_scan_threads   = var.owasp_zap_scan_threads

    cluster         = var.scanning_tools_cluster_arn
    security_groups = aws_security_group.security_tools_scanning.id
    subnets         = join(", ", [for subnet in var.private_subnet_ids : format("%q", subnet)])

    min_ecs_capacity = var.min_ecs_capacity
    max_ecs_capacity = var.max_ecs_capacity

    awslogs-region        = "ca-central-1"
    awslogs-stream-prefix = "ecs-runners-nuclei"
    awslogs-group         = aws_cloudwatch_log_group.nuclei-log.name
  }
}