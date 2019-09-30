#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`
export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}

if [ "$DEPLOY_ENV" != "staging" ] && [ "$DEPLOY_ENV" != "prod" ]; then
  echo "Error: DEPLOY_ENV must be set to 'staging' or 'prod'."
  exit 1
fi

# Deploys a new staging publisher-base docker image to the City of Austin dockerhub
TAG="cityofaustin/branch-publisher-base:$DEPLOY_ENV-latest"
docker build -f $CD/branch-publisher-base.Dockerfile -t $TAG $CD
docker push $TAG

# cityofaustin/branch-publisher-base is used exclusively by codebuild as the base image to build new branch-publisher images.
# When this image gets updated, codebuild needs to re-download it from dockerhub.
# So we clear out our CodeBuild docker image cache (to clear out the old cityofaustin/branch-publisher-base image layer)

# Remove codebuild docker image cache
echo "Clearing codebuild image cache"
aws codebuild update-project \
  --name coa-branch-publisher-builder-$DEPLOY_ENV \
  --cache type=NO_CACHE \
> /dev/null

# Strangely, you can't set Local cache modes with `aws codebuild update-project`.
# It only accepts "type" and "location" as cache options, not "mode(s)".
# Had to use boto3 in python to update --cache type=LOCAL,modes=[LOCAL_DOCKER_LAYER_CACHE]
# pipenv run python $CD/enable_cache.py

aws codebuild update-project \
  --name coa-branch-publisher-builder-$DEPLOY_ENV \
  --cache type=LOCAL,modes=[LOCAL_DOCKER_LAYER_CACHE] \
> /dev/null

echo "done!"
