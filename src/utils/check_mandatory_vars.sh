#!/usr/bin/env bash

if [[ -z "$DEPLOY_ENV" ]]; then
  echo "Error: missing required DEPLOY_ENV environment variable."
  exit 1
fi

if [[ -z "$AWS_REGION" ]]; then
  echo "Error: missing required AWS_REGION environment variable."
  exit 1
fi
