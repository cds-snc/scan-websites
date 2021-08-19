# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="14"
ARG DISTRO_VERSION="3.12"

# Stage 1 - bundle base image + runtime
# Grab a fresh copy of the image and install GCC
FROM node:${RUNTIME_VERSION}-alpine${DISTRO_VERSION} AS node-alpine

# Install GCC (Alpine uses musl but we compile and link dependencies with GCC)
RUN apk add --no-cache \
    libstdc++ \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

# Stage 2 - build function and dependencies
FROM node-alpine AS build-image

# Install aws-lambda-cpp build dependencies
RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    libexecinfo-dev \
    make \
    cmake \
    libcurl \
    python3

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy handler function
COPY . ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

RUN npm install
RUN npm install -g typescript
RUN make build

# Install Lambda Runtime Interface Client for Python
RUN npm install aws-lambda-ric

# Stage 3 - final runtime image

# Grab a fresh copy of the Python image
FROM node-alpine

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR}/node_modules ${FUNCTION_DIR}/node_modules
COPY --from=build-image ${FUNCTION_DIR}/dist ${FUNCTION_DIR}

# Set build variables
ARG git_sha 
ENV GIT_SHA=$git_sha

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ARG RIE_VERSION=1.1
RUN wget -O aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/download/${RIE_VERSION}/aws-lambda-rie \
    && mv aws-lambda-rie /usr/bin/aws-lambda-rie
COPY bin/entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh

ENTRYPOINT [ "/entry.sh" ]
CMD [ "index.handler" ]
