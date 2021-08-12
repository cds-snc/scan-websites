#!/bin/bash

docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:v0.7.2 -P ./bin/ -x ./.github/workflows/scripts/*.sh