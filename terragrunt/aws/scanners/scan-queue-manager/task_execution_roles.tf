###
# The task execution role grants the Amazon ECS container and Fargate agents 
# permission to make AWS API calls on your behalf
###

resource "aws_iam_role" "task_execution_role_sqm" {
  name               = "security_tools_execution_role_sqm"
  assume_role_policy = data.aws_iam_policy_document.task_execution_role_sqm.json
}

resource "aws_iam_role_policy_attachment" "scan_queue_manager_policies" {
  role       = aws_iam_role.task_execution_role_sqm.name
  policy_arn = aws_iam_policy.scan_queue_manager_policies.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_policies" {
  role       = aws_iam_role.task_execution_role_sqm.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}


###
# Policies
###
resource "aws_iam_policy" "scan_queue_manager_policies" {
  name   = "ScanQueueManagerTaskExecutionPolicies"
  path   = "/"
  policy = data.aws_iam_policy_document.scan_queue_manager_container_policies.json
}