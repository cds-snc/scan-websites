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
laws s3api create-bucket --bucket axe-core-report-data
laws s3api create-bucket --bucket axe-core-screenshots
laws s3api create-bucket --bucket owasp-zap-report-data

printf "Sample data begin..."
# create tmp directory to put sample data after chunking
mkdir -p /tmp/localstack/data

# Grant bucket public read
laws s3api put-bucket-acl --bucket axe-core-report-data --acl public-read-write
laws s3api put-bucket-acl --bucket axe-core-screenshots --acl public-read-write
laws s3api put-bucket-acl --bucket owasp-zap-report-data --acl public-read-write

printf "Creating SNS topic..."
laws sns create-topic --name axe-core-urls-topic
laws sns create-topic --name dynamic-scan-urls-topic
laws sns create-topic --name s3-event-topic

printf "Create a pass through topic"
laws s3api put-bucket-notification-configuration --bucket axe-core-report-data --notification-configuration file://notification.json
laws s3api put-bucket-notification-configuration --bucket owasp-zap-report-data --notification-configuration file://notification.json

printf "Add subscriptions to topics"
laws sns subscribe --topic-arn arn:aws:sns:ca-central-1:000000000000:axe-core-urls-topic --protocol http --notification-endpoint "http://scanner-axe:8080/2015-03-31/functions/function/invocations"
laws sns subscribe --topic-arn arn:aws:sns:ca-central-1:000000000000:dynamic-scan-urls-topic --protocol http --notification-endpoint "http://scanner-axe:8080/2015-03-31/functions/function/invocations"
laws sns subscribe --topic-arn arn:aws:sns:ca-central-1:000000000000:s3-event-topic --protocol http --notification-endpoint "http://app:8000/dev/handle_s3_event"

set +x
