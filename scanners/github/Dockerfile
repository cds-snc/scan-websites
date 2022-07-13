FROM golang:1.18.3-alpine@sha256:7cc62574fcf9c5fb87ad42a9789d5539a6a085971d58ee75dd2ee146cb8a8695 as build

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
FROM alpine:latest

COPY --from=build /main /main

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY bin/entry.sh /
RUN chmod 755 /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD ["/main"]