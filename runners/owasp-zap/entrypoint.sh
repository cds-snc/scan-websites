#!/bin/sh -l

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

# Timeout scan after 1 hour to prevent running indefinitely if the OWASP ZAP container crashes
timeout 1h zap-cli --port "${ZAP_PORT}" --zap-url "http://$HOST_IP" active-scan --recursive "${SCAN_URL}"

high_alerts=$(curl "http://$HOST_IP:${ZAP_PORT}/JSON/alert/view/alertsSummary/?baseurl=${SCAN_URL}" | jq -r '.alertsSummary.High')

echo "high alerts are $high_alerts"

curl "http://$HOST_IP:${ZAP_PORT}/OTHER/core/other/jsonreport/" | jq . > zap-scan-results.json

if [[ -z "${PUSH_TO_SECURITYHUB}" ]]; then
  IMPORTVULTOSECURITYHUB=false
else
  IMPORTVULTOSECURITYHUB=true
fi

jq "{ \"messageType\": \"ScanReport\", \"reportType\": \"OWASP-Zap\", \"createdAt\": $(date +\"%Y-%m-%dT%H:%M:%S\"),\"importToSecurityhub\": \"$IMPORTVULTOSECURITYHUB\",\"url\": \"$SCAN_URL\",\"s3Bucket\": \"${S3_BUCKET}\",\"key\": \"Reports/$FILENAME.xml\", \"report\": . }" zap-scan-results.json > payload.json

aws s3 cp payload.json s3://"${S3_BUCKET}"/Reports/"$FILENAME".json
