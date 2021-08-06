#!/bin/bash

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
    --payload '{ "task": "migrate" }' \
    --region ca-central-1 \
    response
  test_migrate_resp response
}
