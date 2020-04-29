#!/usr/bin/env bash
set -e
D=`dirname $BASH_SOURCE`
PREV_D=$(pwd)
JANIS_D=$D/../janis

function print_var {
  echo "##### $1: [${!1}]"
}

echo "##### Printing environment variables used for react-static build [$BUILD_ID]"
print_var "DEPLOY_ENV"
print_var "JANIS_BRANCH"
print_var "BUILD_ID"
print_var "DEPLOYMENT_MODE"
print_var "CMS_API"
print_var "CMS_MEDIA"
print_var "CMS_DOCS"
print_var "NETLIFY_SITE_NAME"
print_var "GOOGLE_ANALYTICS"

# S3_BUCKET is where react-static build output is placed.
# Production and Staging sites are hosted directly from their S3_BUCKET.
# Review sites are hosted on netlify, but we store build output in S3 to allow incremental builds.
case "${DEPLOY_ENV}" in
  production)
    S3_BUCKET=s3://coa-janis-austin-gov-production
  ;;
  staging)
    S3_BUCKET=s3://coa-janis-austin-gov-staging
  ;;
  *)
    S3_BUCKET=s3://coa-publisher/builds/$DEPLOY_ENV/$JANIS_BRANCH
  ;;
esac
print_var "S3_BUCKET"

if [ "$BUILD_TYPE" == "rebuild" ]; then
  echo "##### Starting react-static build"
  SECONDS=0 # This is a bash builtin variable that tracks the number of seconds passed
  cd $JANIS_D # build-css has some relative path logic that requires us to be inside the janis/ directory during the build process
  export NODE_PATH=./src
  yarn npm-run-all build-css build-js
  duration=$SECONDS
  cd $PREV_D
  echo "##### Completed react-static build in $(($duration / 60)):$(($duration % 60))"
else
  # Non-rebuild BUILD_TYPES are incremental
  # We download the existing react-static output and create incremental updates
  echo "##### Downloading cached react-static output from S3"
  SECONDS=0
  aws s3 sync $S3_BUCKET $JANIS_D/dist --only-show-errors --delete
  duration=$SECONDS
  echo "##### Completed download from S3 in $(($duration / 60)):$(($duration % 60))"

  echo "##### Starting react-static incremental build"
  SECONDS=0
  cd $JANIS_D
  export NODE_PATH=./src
  yarn npm-run-all build-css build-js-incremental
  duration=$SECONDS
  cd $PREV_D
  echo "##### Completed react-static incremental build in $(($duration / 60)):$(($duration % 60))"
fi

echo "##### Uploading to S3"
SECONDS=0
aws s3 sync $JANIS_D/dist $S3_BUCKET --only-show-errors --delete
duration=$SECONDS
echo "##### Completed upload to S3 in $(($duration / 60)):$(($duration % 60))"

case "${DEPLOY_ENV}" in
  staging|production)
    # Create a cache invalidation for the Cloudfront Distribution pointing to S3_BUCKET
    # TODO: have specific invalidation paths for incremental builds?
    aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*";
  ;;
  *)
    # Review sites are deployed to netlify
    SECONDS=0
    node $D/deployToNetlify.js "$NETLIFY_SITE_NAME" "$JANIS_D/dist"
    duration=$SECONDS
    echo "##### Completed deployment to Netlify in $(($duration / 60)):$(($duration % 60))"
  ;;
esac

rm -rf $JANIS_D/dist
echo "##### Successfully finished build [$BUILD_ID]"
