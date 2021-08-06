#!/bin/bash

# shellcheck disable=SC1091
source .github/workflows/scripts/migrate.sh

RETVAL=0

# reports the status of the return value of a function you can use
# $? to capture that but it must be on the next executed line of the script
function t {
  if [[ $1 == 0 ]]; then
    echo "🟩 passed"
  else
    echo "🟥 failed"
    RETVAL=1
  fi 
}

echo "Testing Success Response"
test_migrate_resp .github/workflows/scripts/test/response
t $?

echo "Testing Failure Response"
! test_migrate_resp .github/workflows/scripts/test/failed_response
t $?

exit $RETVAL
