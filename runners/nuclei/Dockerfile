FROM golang:1.18.3-alpine@sha256:7cc62574fcf9c5fb87ad42a9789d5539a6a085971d58ee75dd2ee146cb8a8695 as build-env

RUN apk update && apk upgrade

RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

FROM alpine:3.16

ARG GLIBC_VER=2.31-r0
ARG AWS_CLI_VERSION="2.2.29"

RUN apk add --no-cache curl binutils jq

WORKDIR /tmp 

RUN curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip -o awscliv2.zip
RUN unzip -q awscliv2.zip

RUN apk add --no-cache bind-tools ca-certificates chromium

ARG GLIBC_SRC=https://github.com/sgerrand/alpine-pkg-glibc/releases/download

RUN curl -sL https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub -o /etc/apk/keys/sgerrand.rsa.pub
RUN curl -sLO ${GLIBC_SRC}/${GLIBC_VER}/glibc-${GLIBC_VER}.apk
RUN curl -sLO ${GLIBC_SRC}/${GLIBC_VER}/glibc-bin-${GLIBC_VER}.apk
RUN apk add --no-cache glibc-${GLIBC_VER}.apk glibc-bin-${GLIBC_VER}.apk

COPY --from=build-env /go/bin/nuclei /usr/local/bin/nuclei
RUN aws/install
RUN rm -rf \
    awscliv2.zip \
    aws \
    /usr/local/aws-cli/v2/*/dist/aws_completer \
    /usr/local/aws-cli/v2/*/dist/awscli/data/ac.index \
    /usr/local/aws-cli/v2/*/dist/awscli/examples

WORKDIR /scan

COPY entrypoint.sh /entrypoint.sh

# Launch nuclei scan
ENTRYPOINT ["/entrypoint.sh"]