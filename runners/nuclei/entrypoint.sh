#!/bin/sh -l

nuclei --version

date=$(date +\"%Y-%m-%dT%H:%M:%S:%N\")
fDate=$(echo "$date" | sed -e 's/[^A-Za-z0-9._-]/_/g')

# Convert URL into a valid filename for the report
FILENAME=$(echo "$SCAN_URL" | sed -e 's/[^A-Za-z0-9._-]/_/g')-$fDate

nuclei -u "${SCAN_URL}" -severity critical,high,medium -o nuclei-results_lines.json --json
jq --slurp . < nuclei-results_lines.json > nuclei-results.json

if [[ -z "${PUSH_TO_SECURITYHUB}" ]]; then
  IMPORTVULTOSECURITYHUB=false
else
  IMPORTVULTOSECURITYHUB=true
fi

jq "{ \"messageType\": \"ScanReport\", \"reportType\": \"Nuclei\", \"createdAt\": $(date +\"%Y-%m-%dT%H:%M:%S\"),\"importToSecurityhub\": \"$IMPORTVULTOSECURITYHUB\",\"id\": \"$SCAN_ID\",\"url\": \"$SCAN_URL\",\"s3Bucket\": \"${S3_BUCKET}\",\"key\": \"Reports/$FILENAME.json\", \"report\": . }" nuclei-results.json > payload.json
aws s3 cp payload.json s3://"${S3_BUCKET}"/Reports/"$FILENAME".json