#!/bin/bash

echo hitting app root endpoint
curl "http://api:8080/2015-03-31/functions/function/invocations" -d '{
    "resource": "/",
    "path": "/organization",
    "requestContext": {},
    "httpMethod": "POST",
    "headers": {},
    "multiValueHeaders": { },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "body": "{\"name\": \"cheese\"}",
    "isBase64Encoded": false
}' |jq
