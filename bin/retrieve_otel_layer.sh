#!/bin/bash

aws lambda get-layer-version-by-arn \
--region ca-central-1 \
--arn arn:aws:lambda:ca-central-1:901920570463:layer:aws-otel-python38-ver-1-7-1:1 \
| jq -r '.Content.Location' \
| xargs curl -o ../api/otel-layer.zip