# Readme Scanner

```gql
{
  repository(name: "covid-alert-server", owner: "cds-snc") {
    codeOfConduct {
      name
    }
    description
    licenseInfo {
      spdxId
    },
    securityPolicyUrl,
    isSecurityPolicyEnabled,
    forkingAllowed,
    fundingLinks {
      url
    }
    defaultBranchRef {
      name,
      branchProtectionRule {
        isAdminEnforced
        requiresStatusChecks
        requiresApprovingReviews
        requiresCommitSignatures
      }
    }
  }
}

```