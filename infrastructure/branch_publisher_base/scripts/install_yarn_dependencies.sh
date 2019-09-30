#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`

# Use cached node_modules if a cache exists and the yarn.lock is unchanged.
if [[ $(python $CD/cache_exists.py) == "True" ]]; then
  aws s3 cp --recursive s3://coa-publisher-codebuild/cache/$JANIS_BRANCH/yarn.lock ./cache
  yarn_lock_diff=$(diff <(md5sum cache/yarn.lock) <(md5sum janis/yarn.lock))
  if [ "$yarn_lock_diff" = "" ]; then
    echo "yarn.lock unchanged. Using cached node_modules/"
    aws s3 cp --recursive s3://coa-publisher-codebuild/cache/$JANIS_BRANCH/node_modules.tar.gz ./janis
    tar -xzvf ./janis/node_modules.tar.gz -C ./janis
    rm ./janis/node_modules.tar.gz
    exit 0
  fi
fi

# Install node_modules and add them to the cache
yarn install --cwd ./janis
# Add node_modules to cache
tar -czf node_modules.tar.gz -C janis ./node_modules
aws s3 cp ./node_modules.tar.gz s3://coa-publisher-codebuild/cache/$JANIS_BRANCH/node_modules.tar.gz
rm node_modules.tar.gz
# Add yarn.lock to cache
aws s3 cp ./janis/yarn.lock s3://coa-publisher-codebuild/cache/$JANIS_BRANCH/yarn.lock
