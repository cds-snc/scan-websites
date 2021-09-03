#!/bin/bash

echo hitting api crawl endpoint
curl "http://api:8080/2015-03-31/functions/function/invocations" -d '{
    "resource": "/",
    "path": "/scans/crawl",
    "requestContext": {},
    "httpMethod": "POST",
    "headers": {},
    "multiValueHeaders": { },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "body": "{ \"url\" : \"https://www.example.com\" }",
    "isBase64Encoded": false
}' |jq
