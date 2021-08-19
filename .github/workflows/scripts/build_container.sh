#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

GITHUB_SHA=$1
REGISTRY=$2
IMAGE=$3

EXTRA_ARGS=()
if [[ "$IMAGE" == "scanners/axe-core" ]];
then
  EXTRA_ARGS+=(--build-arg CHROMIUM=with-chromium)
fi

DOCKER_FILE="Dockerfile"
if [[ $IMAGE == scanners/* ]];
then
  DOCKER_FILE=scanners/Dockerfile
else
  cd "${IMAGE}" || exit 3
fi

docker --debug build \
    -f $DOCKER_FILE \
    -t "${REGISTRY}/${IMAGE}:latest" \
    --build-arg IMAGE_NAME="${IMAGE}" \
    --build-arg git_sha="${GITHUB_SHA}" \
    "${EXTRA_ARGS[@]}" \
    .