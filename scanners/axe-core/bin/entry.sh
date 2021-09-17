#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then

    # exec /usr/bin/aws-lambda-rie /usr/local/bin/npx aws-lambda-ric "$1"
    # Watch all javascript, typescript and json files and reload if any of them change
    apk add cmake cmake-doc extra-cmake-modules extra-cmake-modules-doc make
    cd /function || exit
    make install-dev
    
    exec /local.sh "$1"
else
    exec /usr/local/bin/npx aws-lambda-ric "$1"
fi