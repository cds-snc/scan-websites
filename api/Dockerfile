FROM amazon/aws-lambda-python:3.8

# Define function directory
ARG FUNCTION_DIR="/function"

RUN yum -y install \
    ca-certificates \
    curl \
    git \
    gstreamer1.0-libav \
    libnss3-tools \
    libatk-bridge2.0-0 \
    libcups2-dev \
    libxkbcommon-x11-0 \
    libxcomposite-dev \
    libxrandr2 \
    libgbm-dev \
    libgtk-3-0 \
    libxshmfence-dev \
    gnupg2 \
    postgresql-client \
    openssh-client \
    python3-pip \
    unzip \
    vim \
    wget \
    xz-utils \
    zsh \
    entr \
    && yum -y autoremove \
    && yum clean all

WORKDIR ${FUNCTION_DIR}

RUN mkdir -p /pymodules
ENV PYTHONPATH=/pymodules
ENV PLAYWRIGHT_BROWSERS_PATH=/pymodules/playwright

COPY ./requirements_playwright.txt ${FUNCTION_DIR}

RUN python -m pip install -r ${FUNCTION_DIR}/requirements_playwright.txt

COPY ./requirements.txt ${FUNCTION_DIR}

RUN python -m pip install -r ${FUNCTION_DIR}/requirements.txt --target /pymodules

RUN playwright install chromium

# Copy function code
COPY . ${FUNCTION_DIR}

RUN unzip otel-layer.zip -d /opt && rm otel-layer.zip

# Set build variables
ARG git_sha
ENV GIT_SHA=$git_sha

CMD [ "main.handler" ]
