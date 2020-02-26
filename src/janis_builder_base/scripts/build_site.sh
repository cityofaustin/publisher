#!/usr/bin/env bash
set -e
D=`dirname $BASH_SOURCE`
PREV_D=$(pwd)
JANIS_D=$D/../janis

function clean_up {
  cd $PREV_D
}
trap clean_up EXIT

function print_var {
  echo "##### $1: [${!1}]"
}

echo "##### Printing environment variables used for react-static build [$BUILD_ID]"
print_var "JANIS_BRANCH"
print_var "BUILD_ID"
print_var "DEPLOYMENT_MODE"
print_var "CMS_API"
print_var "CMS_MEDIA"
print_var "CMS_DOCS"

echo "##### Starting react-static build"
SECONDS=0 # This is a bash builtin variable that tracks the number of seconds passed
cd $JANIS_D
export NODE_PATH="./src"
yarn npm-run-all build-css build-js
duration=$SECONDS
echo "##### Completed react-static build in $(($duration / 60)):$(($duration % 60))"

# TODO: compress dist/ folder for PR builds?

echo "##### Uploading to S3"
SECONDS=0
zipped_site="janis#$JANIS_BRANCH.zip"
zip -rq $zipped_site ./dist/*
aws s3 cp ./$zipped_site s3://coa-publisher/builds/$DEPLOY_ENV/$zipped_site --no-progress
# TODO: for production and staging
# aws s3 sync ./dist s3://coa-publisher/builds/$DEPLOY_ENV/$JANIS_BRANCH --no-progress --delete
duration=$SECONDS
echo "##### Completed upload to S3 in $(($duration / 60)):$(($duration % 60))"

echo "##### Successfully finished build [$BUILD_ID]"
