#!/bin/bash
# Note, this file isn't executed, it's sourced. So, skip strict bash commands in here
# as they'll terminate the shell.

echo "Sourcing migrate.sh"
function test_migrate_resp {
  if [[ $(cat "$1") =~ $(cat .github/workflows/scripts/expected_response.json) ]]; then
    echo "Migration Success"
    return 0
  fi
  echo "Migration Error"
  return 1
}

function migrate {
  aws lambda invoke \
    --function-name api \
    --cli-binary-format raw-in-base64-out \
    --payload '{ "task": "migrate" }' \
    --region ca-central-1 \
    response
  test_migrate_resp response
}
