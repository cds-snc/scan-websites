ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Set these in devcontainer.json
ARG SHELLCHECK_VERSION
ARG SHELLCHECK_CHECKSUM
ARG TERRAFORM_VERSION
ARG TERRAFORM_CHECKSUM
ARG TERRAGRUNT_VERSION
ARG TERRAGRUNT_CHECKSUM

# Install packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    && apt-get autoremove -y && apt-get clean -y

# Install Terraform
ARG TERRAFORM_SRC=https://releases.hashicorp.com/terraform
RUN curl -Lo terraform.zip "${TERRAFORM_SRC}/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
    && echo "${TERRAFORM_CHECKSUM} terraform.zip" | sha256sum --check \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

# Install Terragrunt
ARG TERRAGRUNT_SRC=https://github.com/gruntwork-io/terragrunt/releases/download
RUN curl -Lo terragrunt ${TERRAGRUNT_SRC}/v"${TERRAGRUNT_VERSION}"/terragrunt_linux_"$(dpkg --print-architecture)" \
    && echo "${TERRAGRUNT_CHECKSUM} terragrunt" | sha256sum --check \
    && chmod +x terragrunt \
    && mv terragrunt /usr/local/bin/

# Install ShellCheck
ARG SHELLCHECK_SRC=https://github.com/koalaman/shellcheck/releases/download
RUN curl -Lo shellcheck.tar.xz "${SHELLCHECK_SRC}/v${SHELLCHECK_VERSION}/shellcheck-v${SHELLCHECK_VERSION}.linux.x86_64.tar.xz" \
    && echo "${SHELLCHECK_CHECKSUM} shellcheck.tar.xz" | sha256sum --check \
    && tar -xf shellcheck.tar.xz \
    && mv "shellcheck-v${SHELLCHECK_VERSION}/shellcheck" /usr/local/bin/ \
    && rm -r shellcheck*

# Install Checkov
RUN pip3 install --upgrade requests setuptools \
    && pip3 install --upgrade botocore checkov

# Install AWS CLI
ARG AWS_CLI_VERSION
ARG AWS_SRC=https://awscli.amazonaws.com
COPY .devcontainer/aws_cli.asc ./
RUN curl -Lo awscliv2.zip "${AWS_SRC}/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" \
    && curl -Lo awscliv2.sig "${AWS_SRC}/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip.sig" \
    && gpg --import ./aws_cli.asc \
    && gpg --verify awscliv2.sig awscliv2.zip \
    && unzip awscliv2.zip \
    && ./aws/install -i /usr/local/aws-cli -b /usr/local/bin

ARG GO_VERSION
ENV GOROOT=/usr/local/go

RUN wget https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -xvf go${GO_VERSION}.linux-amd64.tar.gz \
    && mv go /usr/local \
    && rm go${GO_VERSION}.linux-amd64.tar.gz

COPY .devcontainer/apt-packages.txt ./
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && xargs apt-get -y install --no-install-recommends < apt-packages.txt

# Setup aliases and autocomplete
RUN echo "\n\
complete -C /usr/bin/aws_completer aws\n\
complete -C /usr/local/bin/terraform terraform\n\
complete -C /usr/local/bin/terraform terragrunt\n\
alias tf='terraform'\n\
alias tg='terragrunt'\n\
alias ll='la -la' \n\
alias laws='aws --endpoint-url=http://localstack:4566 --region=ca-central-1'" >> /home/vscode/.zshrc

# Setup AWS Credentials
RUN mkdir -p /home/vscode/.aws

RUN echo "\n\
[default]\n\
aws_access_key_id=foo\n\
aws_secret_access_key=bar\n\
" >> /home/vscode/.aws/credentials

RUN echo "\n\
[default]\n\
region=ca-central-1\n\
output=json\n\
" >> /home/vscode/.aws/config

RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g typescript" 2>&1
