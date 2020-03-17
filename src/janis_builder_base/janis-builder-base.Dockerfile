FROM node:12.14.1-alpine3.11

# Install other dependencies
RUN apk add --no-cache --upgrade \
  git \
  bash \
  zip

# Install aws-cli
RUN apk -v --update add \
    python \
    py-pip \
    groff \
    less \
    mailcap \
    && \
  pip --no-cache-dir install --upgrade awscli==1.16.248 && \
  apk -v --purge del py-pip && \
  rm -rf /var/cache/apk/*

# Set DEPLOY_ENV
ARG DEPLOY_ENV
ENV DEPLOY_ENV=$DEPLOY_ENV

# Create directories
RUN mkdir src
RUN mkdir src/cache
RUN mkdir src/scripts
WORKDIR /src

# Copy scripts into /src
COPY "./scripts" ./scripts

# Install dependencies for scripts
COPY "./package.json" ./scripts
RUN yarn install --cwd ./scripts
