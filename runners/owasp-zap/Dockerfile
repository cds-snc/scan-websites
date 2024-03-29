FROM python:3.8-alpine@sha256:cd2afe99fc96d851a30ee3956a3e12c78c0fe766ab4afd47f96e5ca1a94dc62d

WORKDIR /scan

ARG GLIBC_VER=2.31-r0
ARG AWS_CLI_VERSION="2.2.29"

RUN apk update && apk upgrade

RUN apk add --no-cache curl binutils bash jq

ARG GLIBC_SRC=https://github.com/sgerrand/alpine-pkg-glibc/releases/download

RUN curl -sL https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub -o /etc/apk/keys/sgerrand.rsa.pub
RUN curl -sLO ${GLIBC_SRC}/${GLIBC_VER}/glibc-${GLIBC_VER}.apk
RUN curl -sLO ${GLIBC_SRC}/${GLIBC_VER}/glibc-bin-${GLIBC_VER}.apk
RUN apk add --force-overwrite --no-cache glibc-${GLIBC_VER}.apk glibc-bin-${GLIBC_VER}.apk

RUN curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip -o awscliv2.zip
RUN unzip awscliv2.zip
RUN aws/install
RUN rm -rf \
    awscliv2.zip \
    aws \
    /usr/local/aws-cli/v2/*/dist/aws_completer \
    /usr/local/aws-cli/v2/*/dist/awscli/data/ac.index \
    /usr/local/aws-cli/v2/*/dist/awscli/examples

RUN pip install --upgrade zapcli

COPY entrypoint.sh /entrypoint.sh

# Launch OWASP scan
ENTRYPOINT ["/entrypoint.sh"]