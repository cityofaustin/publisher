#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`

# Allows us to use BUILDKIT features like adding a --target to docker build
# Only works for "docker build" not "docker-compose ... --build"
export DOCKER_BUILDKIT=1
