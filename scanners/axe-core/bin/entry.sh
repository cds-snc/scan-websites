#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then

    # exec /usr/bin/aws-lambda-rie /usr/local/bin/npx aws-lambda-ric "$1"
    # Watch all javascript, typescript and json files and reload if any of them change
    exec /local.sh "$1"
else
    exec /usr/local/bin/npx aws-lambda-ric "$1"
fi