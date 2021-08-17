FROM python:3.8-alpine

WORKDIR /scan

RUN apk update \
    && apk upgrade \
    && apk add --update curl bash jq

RUN pip install --upgrade zapcli

# Install AWS CLI
ARG AWS_CLI_VERSION="2.2.29"
RUN curl -Lo awscliv2.zip "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" \
    && unzip awscliv2.zip \
    && ./aws/install -i /usr/local/aws-cli -b /usr/local/bin

COPY entrypoint.sh /entrypoint.sh

# Launch OWASP scan
ENTRYPOINT ["/entrypoint.sh"]
