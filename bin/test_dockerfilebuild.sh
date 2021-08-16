#!/bin/bash

# Create a docker ignore to speed up context
cat << EOF > .dockerignore
*
!.devcontainer
EOF

DOCKER_BUILDKIT=0 docker build . -f .devcontainer/Dockerfile \
  -t foo:bar \
  --build-arg VARIANT="3.9" \
  --build-arg INSTALL_NODE="true" \
  --build-arg NODE_VERSION="lts/*" \
  --build-arg SHELLCHECK_VERSION="0.7.2" \
  --build-arg SHELLCHECK_CHECKSUM="70423609f27b504d6c0c47e340f33652aea975e45f312324f2dbf91c95a3b188" \
  --build-arg TERRAFORM_VERSION="1.0.3" \
  --build-arg TERRAFORM_CHECKSUM="99c4866ffc4d3a749671b1f74d37f907eda1d67d7fc29ed5485aeff592980644" \
  --build-arg TERRAGRUNT_VERSION="0.31.1" \
  --build-arg TERRAGRUNT_CHECKSUM="76b253919ad688025a4a37338e5602543b0426cae1be1f863b4f3d60dd95ac28" \
  --build-arg AWS_CLI_VERSION="2.2.29"
rm .dockerignore