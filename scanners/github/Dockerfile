FROM golang:1.20.1-alpine@sha256:87d0a3309b34e2ca732efd69fb899d3c420d3382370fd6e7e6d2cb5c930f27f9 as build

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
FROM alpine:latest@sha256:69665d02cb32192e52e07644d76bc6f25abeb5410edc1c7a81a10ba3f0efb90a

COPY --from=build /main /main

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY bin/entry.sh /
RUN chmod 755 /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD ["/main"]