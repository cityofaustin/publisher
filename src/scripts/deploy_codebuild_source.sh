#!/usr/bin/env bash
set -a
D=`dirname $BASH_SOURCE`
source $D/../../.env # Source environment variables
sh $D/../utils/check_mandatory_vars.sh

# Sync files to be used as codebuild source
# codebuild looks in S3 to get the Dockerfile used to build branch-publisher containers
# Run this step whenever /source/buildspec.yml or /source/janis-builder.Dockerfile change
S3_DESTINATION="s3://coa-publisher/janis_builder_factory_source/$DEPLOY_ENV"
echo "Syncing local source into $S3_DESTINATION"
pipenv run aws s3 sync $D/../janis_builder_factory_source $S3_DESTINATION --delete
