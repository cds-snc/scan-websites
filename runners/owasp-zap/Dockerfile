FROM python:3.8-alpine

WORKDIR /scan

RUN apk update \
    && apk upgrade \
    && apk add --update curl bash jq

RUN pip install --upgrade zapcli awscli
COPY entrypoint.sh /entrypoint.sh

# Launch OWASP scan
ENTRYPOINT ["/entrypoint.sh"]
