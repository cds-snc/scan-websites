#!/bin/bash

set -x

GITHUB_SHA=$1
REGISTRY=$2
IMAGE=$3

EXTRA_ARGS=
if [[ "$IMAGE" == "scanners/axe-core" ]];
then
  EXTRA_ARGS="$EXTRA_ARGS --build-arg CHROMIUM='with-chromium'"
fi

if [[ $IMAGE == scanners/* ]];
then
  cd ../..
  EXTRA_ARGS="$EXTRA_ARGS --build-arg SCANNER_NAME='$IMAGE'"
fi

docker build \
    -f scanners/Dockerfile \
    -t "$REGISTRY/$IMAGE:latest" \
    --build-arg git_sha="$GITHUB_SHA" \
    $EXTRA_ARGS \
    .
