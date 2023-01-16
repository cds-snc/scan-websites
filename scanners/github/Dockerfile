FROM golang:1.19.5-alpine@sha256:2381c1e5f8350a901597d633b2e517775eeac7a6682be39225a93b22cfd0f8bb as build

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
FROM alpine:latest@sha256:f271e74b17ced29b915d351685fd4644785c6d1559dd1f2d4189a5e851ef753a

COPY --from=build /main /main

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY bin/entry.sh /
RUN chmod 755 /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD ["/main"]