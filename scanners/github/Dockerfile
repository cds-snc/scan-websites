FROM golang:1.20.2-alpine@sha256:87734b78d26a52260f303cf1b40df45b0797f972bd0250e56937c42114bf472c as build

# This is needed or the build will fail with the following error: 
# $GOPATH/go.mod exists but should not
WORKDIR /app

# cache dependencies
COPY go.mod ./
COPY go.sum ./
RUN  go mod download
# build
COPY *.go ./
RUN  go build -o /main
# copy artifacts to a clean image
FROM alpine:latest@sha256:124c7d2707904eea7431fffe91522a01e5a861a624ee31d03372cc1d138a3126

COPY --from=build /main /main

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY bin/entry.sh /
RUN chmod 755 /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD ["/main"]