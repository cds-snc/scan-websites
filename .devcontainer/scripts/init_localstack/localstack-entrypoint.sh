#!/usr/bin/env bash
printf "Configuring localstack components..."
sleep 5;

function laws {
  aws --endpoint-url=http://localstack:4566 --region=ca-central-1 "$@"
}

set -x

printf "Setting Connection Info..."
laws configure set aws_access_key_id foo
laws configure set aws_secret_access_key bar
laws configure set region ca-central-1
laws configure set output json

printf "Creating bucket..."
laws s3api create-bucket --bucket local-bucket

printf "Sample data begin..."
# create tmp directory to put sample data after chunking
mkdir -p /tmp/localstack/data

# Grant bucket public read
laws s3api put-bucket-acl --bucket local-bucket --acl public-read-write

printf "Creating SNS topic..."
laws sns create-topic --name axe-core-urls-topic

set +x