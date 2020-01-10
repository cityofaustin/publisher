FROM node:12.14.1-alpine3.11

# Install other dependencies
RUN apk add --no-cache --upgrade \
  git \
  bash

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
