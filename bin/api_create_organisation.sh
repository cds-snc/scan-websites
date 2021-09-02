#!/bin/bash

echo hitting create organisation endpoint
curl "http://api:8080/2015-03-31/functions/function/invocations" -d '{
    "resource": "/",
    "path": "/api/v1/organisation",
    "requestContext": {},
    "httpMethod": "POST",
    "headers": {},
    "multiValueHeaders": { },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "body": "{\"name\": \"ABCDE\"}",
    "isBase64Encoded": false
}' |jq
