#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`
LOCAL_SOURCE_DIR=$CD/source
export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}

if [ "$DEPLOY_ENV" != "staging" ] && [ "$DEPLOY_ENV" != "prod" ]; then
  echo "Error: DEPLOY_ENV must be set to 'staging' or 'prod'."
  exit 1
fi

# Step 1.
# Sync files to be used as codebuild source
# codebuild looks in S3 to get the Dockerfile used to build branch-publisher containers
S3_DESTINATION="s3://coa-publisher-codebuild/source/$DEPLOY_ENV"
echo "Syncing local source into $S3_DESTINATION"
aws s3 sync $LOCAL_SOURCE_DIR $S3_DESTINATION --delete

# Step 2.
# Build the codebuild project.
# Environment variables will be overwritten as needed to build specific Janis + Joplin combinations
# --capabilities CAPABILITY_NAMED_IAM is a flag that specifies that you want to create a new IAM Role in your stack.
aws cloudformation deploy \
  --stack-name coa-publisher-codebuild-$DEPLOY_ENV \
  --template-file $CD/codebuild_project.yml \
  --parameter-overrides Env=$DEPLOY_ENV \
  --capabilities CAPABILITY_NAMED_IAM
