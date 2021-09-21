#!/bin/sh


while true; do
  find . -type f \( -name "*.json" -o -name "*.js" -o -name "*.ts" \) -o -path ./node_modules -prune  \
          | entr /usr/bin/aws-lambda-rie /usr/local/bin/npx aws-lambda-ric "$1"
  make build
done