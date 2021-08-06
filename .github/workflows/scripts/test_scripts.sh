#!/bin/bash

RETVAL=0

echo "Testing script_tests.sh"
if [ "$(./test_migration_resp.sh ./test/error_response.json)" = 0 ]; then 
  echo "Error Response Failed"
  RETVAL=1
else
  echo "Error Response Passed"
fi 

if [ "$(./test_migration_resp.sh ./test/success_response.json)" = 0 ]; then 
  echo "Success Response Failed"
  RETVAL=1
else
  echo "Success Response Passed"
fi 

exit $RETVAL