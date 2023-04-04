FROM golang:1.20.2-alpine@sha256:87734b78d26a52260f303cf1b40df45b0797f972bd0250e56937c42114bf472c as build-env

RUN apk update && apk upgrade && apk add --no-cache build-base 

RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

FROM alpine:3.17@sha256:124c7d2707904eea7431fffe91522a01e5a861a624ee31d03372cc1d138a3126

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
RUN apk add --no-cache --force-overwrite glibc-${GLIBC_VER}.apk glibc-bin-${GLIBC_VER}.apk

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