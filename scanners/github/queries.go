package main

import (
	"github.com/shurcooL/githubv4"
)

var complianceQuery struct {
	Repository struct {
		CodeOfConduct struct {
			Name githubv4.String
		}
		Description githubv4.String
		LicenseInfo struct {
			SpdxId githubv4.String
		}
		SecurityPolicyUrl       githubv4.String
		IsSecurityPolicyEnabled githubv4.Boolean
		ForkingAllowed          githubv4.Boolean
		FundingLinks            struct {
			Url githubv4.String
		}
		DefaultBranchRef struct {
			Name                 githubv4.String
			BranchProtectionRule struct {
				IsAdminEnforced          githubv4.Boolean
				RequiresStatusChecks     githubv4.Boolean
				RequiresApprovingReviews githubv4.Boolean
				RequiresCommitSignatures githubv4.Boolean
			}
		}
	} `graphql:"repository(name: $Name, owner: $Owner)"`
}
