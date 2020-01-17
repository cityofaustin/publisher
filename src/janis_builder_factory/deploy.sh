#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`
LOCAL_SOURCE_DIR=$CD/source
export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}

if [ "$DEPLOY_ENV" != "staging" ] && [ "$DEPLOY_ENV" != "prod" ]; then
  echo "Error: DEPLOY_ENV must be set to 'staging' or 'prod'."
  exit 1
fi

# Sync files to be used as codebuild source
# codebuild looks in S3 to get the Dockerfile used to build branch-publisher containers
# Run this step whenever /source/buildspec.yml or /source/janis-builder.Dockerfile change
S3_DESTINATION="s3://coa-publisher/janis_builder_factory_source/$DEPLOY_ENV"
echo "Syncing local source into $S3_DESTINATION"
aws s3 sync $LOCAL_SOURCE_DIR $S3_DESTINATION --delete
