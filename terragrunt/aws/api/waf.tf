resource "aws_wafv2_web_acl" "api_waf" {
  # TODO: Create kinesis stream and logging config
  # checkov:skip=CKV2_AWS_31:Kinesis required,will do in seperate PR
  name        = "api_waf"
  description = "WAF for API protection"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"

        scope_down_statement {
          not_statement {
            statement {
              or_statement {
                statement {
                  regex_pattern_set_reference_statement {
                    arn = aws_wafv2_regex_pattern_set.google_auth_uri.arn
                    field_to_match {
                      uri_path {}
                    }
                    text_transformation {
                      type     = "LOWERCASE"
                      priority = 1
                    }
                  }
                }
                statement {
                  regex_pattern_set_reference_statement {
                    arn = aws_wafv2_regex_pattern_set.body_exclusions.arn
                    field_to_match {
                      uri_path {}
                    }
                    text_transformation {
                      type     = "LOWERCASE"
                      priority = 1
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesLinuxRuleSet"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesLinuxRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 5

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "api_rate_limit"
    priority = 101

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 100
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "api_rate_limit"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "api"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_regex_pattern_set" "google_auth_uri" {
  name        = "GoogleAuthUri"
  description = "Regex to match a Google Authentication request"
  scope       = "REGIONAL"

  regular_expression {
    regex_string = "^/auth/google.*$"
  }
}

resource "aws_wafv2_regex_pattern_set" "body_exclusions" {
  name        = "RequestBodyExclusions"
  description = "Regex to match request urls with bodies that will trigger rulesets"
  scope       = "REGIONAL"

  regular_expression {
    regex_string = "^/scans/template/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}/(scan|scan/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12})$"
  }
}

resource "aws_wafv2_web_acl_association" "waf_association" {
  resource_arn = aws_api_gateway_stage.api.arn
  web_acl_arn  = aws_wafv2_web_acl.api_waf.arn
}
