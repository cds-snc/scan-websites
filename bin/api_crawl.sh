#!/bin/bash

echo hitting api crawl endpoint
curl "http://api:8080/2015-03-31/functions/function/invocations" -d '{
    "resource": "/",
    "path": "/crawl",
    "requestContext": {},
    "httpMethod": "POST",
    "headers": {},
    "multiValueHeaders": { },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "body": "{ \"url\" : \"https://x.com\" }",
    "isBase64Encoded": false
}' |jq
