#!/bin/sh -l

trap 'aws stepfunctions send-task-failure --task-token "${TASK_TOKEN_ENV_VARIABLE}" --task-output "Caught SIGTERM signal"' TERM
trap 'aws stepfunctions send-task-failure --task-token "${TASK_TOKEN_ENV_VARIABLE}" --task-output "Caught SIGINT signal"' INT

heartbeat_cmd="while sleep 60; do aws stepfunctions send-task-heartbeat --task-token ${TASK_TOKEN_ENV_VARIABLE}; done"
eval "$heartbeat_cmd" &

# Check if running locally or in ECS
if [[ -z "${ECS_CONTAINER_METADATA_URI}" ]]; then
  # ECS environment variable not detected so use local docker networking
  HOST_IP="172.17.0.1"
else
  # Use ECS host IP
  HOST_IP=$(curl -s "$ECS_CONTAINER_METADATA_URI" | jq -r '.Networks[].IPv4Addresses[0]')
fi

echo "Host ip: $HOST_IP and Port:${ZAP_PORT}"

# Wait for ZAP proxy to init
CHECKS=0
while ! curl -sSf "$HOST_IP":"${ZAP_PORT}" > /dev/null 2>&1
do
	echo "Waiting for proxy to start..."
	sleep 3
  CHECKS=$((CHECKS+1))
  if [ $CHECKS -gt 100 ]
  then
    echo "Proxy failed to start within 5 minutes, exiting"
    exit 1
  fi
done
sleep 3

date=$(date +\"%Y-%m-%dT%H:%M:%S:%N\")
fDate=$(echo "$date" | sed -e 's/[^A-Za-z0-9._-]/_/g')

# Convert URL into a valid filename for the report
FILENAME=$(echo "$SCAN_URL" | sed -e 's/[^A-Za-z0-9._-]/_/g')-$fDate

zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" exclude "^.*/(logout|log-out|signout|sign-out|deconnecter)/?$"
zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" exclude "^.*\.(css|gif|jpe?g|tiff|png|webp|bmp|ico|svg|js|jsx|pdf)$"
zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" open-url "${SCAN_URL}"
zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" spider "${SCAN_URL}"
zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" ajax-spider "${SCAN_URL}"

# Initial scan will exclude sqli since false positivies occur when sqli is run multithreaded
# Gets list of available scans, excludes sqli and converts to csv
all_except_sqli=$(zap-cli --zap-url http://"$HOST_IP" --port "${ZAP_PORT}" scanners list | tail -n +3 | grep -v "SQL Injection" | awk -F ' ' '{print $2}' | awk NF | awk '$1=$1' RS= OFS=,)

# Set scan threads as defined by environment variable
curl "http://${HOST_IP}:${ZAP_PORT}/JSON/ascan/action/setOptionThreadPerHost/" -H 'Content-Type: application/x-www-form-urlencoded' --data-raw "Integer=${SCAN_THREADS}" --compressed

# Timeout scan after 2 hour to prevent running indefinitely if the OWASP ZAP container crashes
timeout 2h zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" active-scan -s "$all_except_sqli" --recursive "${SCAN_URL}"

# Set scan threads to 1 to prevent sqli false positives
curl "http://${HOST_IP}:${ZAP_PORT}/JSON/ascan/action/setOptionThreadPerHost/" -H 'Content-Type: application/x-www-form-urlencoded' --data-raw "Integer=1" --compressed

# Timeout scan after 1 hour to prevent running indefinitely if the OWASP ZAP container crashes
timeout 1h zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" active-scan -s sqli --recursive "${SCAN_URL}"


high_alerts=$(curl "http://$HOST_IP:${ZAP_PORT}/JSON/alert/view/alertsSummary/?baseurl=${SCAN_URL}" | jq -r '.alertsSummary.High')

echo "high alerts are $high_alerts"

curl "http://$HOST_IP:${ZAP_PORT}/OTHER/core/other/jsonreport/" | jq . > zap-scan-results.json

if [[ -z "${PUSH_TO_SECURITYHUB}" ]]; then
  IMPORTVULTOSECURITYHUB=false
else
  IMPORTVULTOSECURITYHUB=true
fi

jq "{ \"messageType\": \"ScanReport\", \"reportType\": \"OWASP-Zap\", \"createdAt\": $(date +\"%Y-%m-%dT%H:%M:%S\"),\"importToSecurityhub\": \"$IMPORTVULTOSECURITYHUB\",\"id\": \"$SCAN_ID\",\"url\": \"$SCAN_URL\",\"s3Bucket\": \"${S3_BUCKET}\",\"key\": \"Reports/$FILENAME.xml\", \"report\": . }" zap-scan-results.json > payload.json

aws s3 cp payload.json s3://"${S3_BUCKET}"/Reports/"$FILENAME".json
aws stepfunctions send-task-success --task-token "${TASK_TOKEN_ENV_VARIABLE}" --task-output file://payload.json
