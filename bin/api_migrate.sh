#!/bin/bash 

echo hitting api version endpoint
curl "http://api:8080/2015-03-31/functions/function/invocations" -d '{
  "task": "migrate"
}' |jq
