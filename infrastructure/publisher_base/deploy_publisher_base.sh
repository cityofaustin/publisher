#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`

# Deploys a new staging publisher-base docker image to the City of Austin dockerhub

TAG="cityofaustin/publisher-base:staging-latest"
CONTEXT=$CD/../..
docker build -f $CD/publisher-base.Dockerfile -t $TAG $CONTEXT
docker push $TAG
