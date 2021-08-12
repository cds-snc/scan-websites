
###
# In App metrics Task Execution Role
###
# The task execution role grants the Amazon ECS container and Fargate agents 
# permission to make AWS API calls on your behalf
###

resource "aws_iam_role" "task_execution_role" {
  name               = "security_tools_execution_role"
  assume_role_policy = data.aws_iam_policy_document.task_execution_role.json
}

resource "aws_iam_role_policy_attachment" "zap_runner_policies" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = aws_iam_policy.zap_runner_policies.arn
}

resource "aws_iam_role_policy_attachment" "falco_policies" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = aws_iam_policy.send_falco_alerts_to_CloudWatch_ecs_task.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_policies" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}


###
# Policies
###
resource "aws_iam_policy" "zap_runner_policies" {
  name   = "OWASPZapTaskExecutionPolicies"
  path   = "/"
  policy = data.aws_iam_policy_document.zap_runner_container_policies.json
}

resource "aws_iam_policy" "send_falco_alerts_to_CloudWatch_ecs_task" {
  name   = "SendAlertToCloudWatchPolicies"
  path   = "/"
  policy = data.aws_iam_policy_document.send_falco_alerts_to_CloudWatch_ecs_task.json
}
