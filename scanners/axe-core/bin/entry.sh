#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    # Watch all javascript, typescript and json files and reload if any of them change
    exec find . -type f \( -name "*.json" -o -name "*.js" -o -name "*.ts" \) -o -path ./node_modules -prune -false  \
        | entr -r /usr/bin/aws-lambda-rie /usr/local/bin/npx aws-lambda-ric "$1"
else
    exec /usr/local/bin/npx aws-lambda-ric "$1"
fi