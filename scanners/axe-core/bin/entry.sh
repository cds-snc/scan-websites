#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    exec /usr/bin/aws-lambda-rie /usr/local/bin/npx aws-lambda-ric $1
else
    exec /usr/local/bin/npx aws-lambda-ric $1
fi