# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="14"
ARG DISTRO_VERSION="3.12"
ARG CHROMIUM="no-chromium"
ARG IMAGE_NAME

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

FROM node-alpine AS node-alpine-with-chromium
RUN apk add --no-cache chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

FROM node-alpine AS node-alpine-no-chromium

# Stage 2 - build function and dependencies
FROM node-alpine-${CHROMIUM} AS build-image

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
ARG IMAGE_NAME

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy handler function
COPY scanners/common.ts.makefile ${FUNCTION_DIR}/scanners/
COPY scanners/tsconfig.json ${FUNCTION_DIR}/scanners/
COPY ${IMAGE_NAME} ${FUNCTION_DIR}/${IMAGE_NAME}

WORKDIR ${FUNCTION_DIR}/${IMAGE_NAME}

RUN make install
RUN make build

# Install Lambda Runtime Interface Client for Python
RUN npm install aws-lambda-ric

# Stage 3 - final runtime image

# Grab a fresh copy of the image
FROM build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR
ARG IMAGE_NAME

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}/${IMAGE_NAME}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR}/${IMAGE_NAME}/node_modules ${FUNCTION_DIR}/${IMAGE_NAME}/node_modules
# Work around docker bug where if the first copy doesn't copy anything the second copy
# will fail even if it copies something.
RUN true
COPY --from=build-image ${FUNCTION_DIR}/${IMAGE_NAME}/dist ${FUNCTION_DIR}/${IMAGE_NAME}

# Set build variables
ARG git_sha 
ENV GIT_SHA=$git_sha

# Install lambda runtime interactive environment
ARG RIE_VERSION=1.1
RUN wget -O aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/download/${RIE_VERSION}/aws-lambda-rie \
    && mv aws-lambda-rie /usr/bin/aws-lambda-rie
COPY ${IMAGE_NAME}/bin/entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh

ENTRYPOINT [ "/entry.sh" ]
CMD [ "index.handler" ]

