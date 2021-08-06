#!/bin/bash

if [ "$(jq .Payload -r < "$1")" = "Error" ]; then
  echo "Migration Error"
  exit 1
fi