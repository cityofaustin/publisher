#!/usr/bin/env bash
set -e
D=`dirname $BASH_SOURCE`
PREV_D=$(pwd)
JANIS_D=$D/../janis

# function clean_up {
#   cd $PREV_D
# }
# trap clean_up EXIT

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
cd $JANIS_D # build-css has some relative path logic that requires us to be inside the janis/ directory during the build process
export NODE_PATH=./src
yarn npm-run-all build-css build-js
duration=$SECONDS
cd $PREV_D
echo "##### Completed react-static build in $(($duration / 60)):$(($duration % 60))"

echo "##### Uploading to S3"
SECONDS=0
# zipped_site="janis#$JANIS_BRANCH.zip"
# zip -rq $zipped_site ./dist/*
# aws s3 cp ./$zipped_site s3://coa-publisher/builds/$DEPLOY_ENV/$zipped_site --no-progress
# TODO: for production and staging
aws s3 sync $JANIS_D/dist s3://coa-publisher/builds/$DEPLOY_ENV/$JANIS_BRANCH --only-show-errors --delete
duration=$SECONDS
echo "##### Completed upload to S3 in $(($duration / 60)):$(($duration % 60))"

case "${DEPLOY_ENV}" in
  staging|production)
    echo "##### TODO"
  ;;
  *)
    SECONDS=0
    node $D/deployToNetlify.js "$NETLIFY_SITE_NAME" "$JANIS_D/dist"
    duration=$SECONDS
    echo "##### Completed deployment to Netlify in $(($duration / 60)):$(($duration % 60))"
  ;;
esac


echo "##### Successfully finished build [$BUILD_ID]"
