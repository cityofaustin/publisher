#!/usr/bin/env bash
D=`dirname $BASH_SOURCE`
export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}

if [ "$DEPLOY_ENV" != "staging" ] && [ "$DEPLOY_ENV" != "prod" ]; then
  echo "Error: DEPLOY_ENV must be set to 'staging' or 'prod'."
  exit 1
fi

# Get Auth token in order to push docker image to ECR
$(aws ecr get-login --no-include-email)

# Get ECR Repo URI from Stack Outputs
pipenv run python $D/get_ecr_uri.py
source $D/ecr_uri.tmp

# Deploys a new staging janis-builder-base docker image to the City of Austin dockerhub
TAG="$JANIS_BUILDER_BASE_ECR_URI:$DEPLOY_ENV-latest"
docker build -f $D/janis-builder-base.Dockerfile -t $TAG $D
docker push $TAG

# janis-builder-base is used exclusively by codebuild as the base image to build new janis-builder images.
# When this image gets updated, codebuild needs to re-download it from dockerhub.
# So we clear out our CodeBuild docker image cache (to clear out the old cityofaustin/janis-builder-base image layer)

# Remove codebuild docker image cache
echo "Clearing codebuild janis-builder-base image cache"
aws codebuild update-project \
  --name coa-publisher-janis-builder-factory-$DEPLOY_ENV \
  --cache type=NO_CACHE \
> /dev/null

aws codebuild update-project \
  --name coa-publisher-janis-builder-factory-$DEPLOY_ENV \
  --cache type=LOCAL,modes=[LOCAL_DOCKER_LAYER_CACHE] \
> /dev/null

echo "done!"
