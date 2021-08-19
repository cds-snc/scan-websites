#!/bin/bash

set -x

GITHUB_SHA=$1
REGISTRY=$2
IMAGE=$3

EXTRA_ARGS=""
if [[ "$IMAGE" == "scanners/axe-core" ]];
then
  EXTRA_ARGS="${EXTRA_ARGS} --build-arg CHROMIUM=with-chromium"
fi

DOCKER_FILE=Dockerfile
if [[ $IMAGE == scanners/* ]];
then
  cd ../..
  DOCKER_FILE=scanners/Dockerfile
fi

docker --debug build \
    -f $DOCKER_FILE \
    -t "${REGISTRY}/${IMAGE}:latest" \
    --build-arg IMAGE_NAME=${IMAGE} \
    --build-arg git_sha=${GITHUB_SHA} \
    $EXTRA_ARGS \
    .
