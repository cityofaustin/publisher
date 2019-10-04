#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`

JANIS_BRANCH="master"
DEST="anywhere"

TAG="cityofaustin/publisher-branch:$JANIS_BRANCH"
CONTEXT="$CD/.."

docker build \
  -f $CD/publisher-branch.Dockerfile \
  -t $TAG \
  --build-arg JANIS_BRANCH=$JANIS_BRANCH \
  --build-arg DEST=$DEST \
  $CONTEXT
