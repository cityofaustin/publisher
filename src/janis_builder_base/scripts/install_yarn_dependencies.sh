#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`

cached_modules="$CD/cache/node_modules.tar.gz"
cached_yarn_lock="$CD/cache/yarn.lock"

function clean_up {
  if [ ! -z "$cached_modules" ]; then
    echo "#### Cleaning up cached node_modules"
    rm $cached_modules
  fi
  if [ ! -z "$cached_yarn_lock" ]; then
    echo "#### Cleaning up cached yarn.lock"
    rm $cached_yarn_lock
  fi
}
trap clean_up EXIT

function upload_cache {
  # Add compressed node_modules to cache
  tar -czf $cached_modules -C janis $CD/node_modules
  aws s3 cp $cached_modules s3://coa-publisher/cache/$JANIS_BRANCH/node_modules.tar.gz
  # Add yarn.lock to cache
  aws s3 cp $CD/janis/yarn.lock s3://coa-publisher/cache/$JANIS_BRANCH/yarn.lock
}

# Use cached node_modules if a cache exists and the yarn.lock is unchanged.
if [[ $(node $CD/cache_exists.js) == "True" ]]; then
  echo "#### cache exists for branch: $JANIS_BRANCH"
  SOURCE_BRANCH=$JANIS_BRANCH
  CURRENT_BRANCH_CACHE=True
else
  # If no node_module cache exists from your branch, check if master's node_modules can be used.
  echo "#### no cache exists for branch: $JANIS_BRANCH. Trying cache for master branch."
  SOURCE_BRANCH=master
  CURRENT_BRANCH_CACHE=False
fi

# Copy down cached yarn.lock
aws s3 cp s3://coa-publisher/cache/$SOURCE_BRANCH/yarn.lock $CD/cache

# Check difference between cached yarn.lock and your branch's yarn.lock
yarn_lock_diff=$(diff <(md5sum $cached_yarn_lock | awk '{ print $1 }') <(md5sum $CD/janis/yarn.lock | awk '{ print $1 }'))

# If there is no difference between the cached yarn.lock and our janis's yarn.lock,
# Then we can use the cached node_modules
if [ "$yarn_lock_diff" = "" ]; then
  echo "#### yarn.lock unchanged. Using cached node_modules."
  aws s3 cp s3://coa-publisher/cache/$SOURCE_BRANCH/node_modules.tar.gz $CD/cache
  tar -xzf $cached_modules -C $CD/janis

  # If we sourced node_modules from master, then instate a new cache for our specific branch
  if [ "$CURRENT_BRANCH_CACHE" = "False" ]; then
    upload_cache
  fi
else
  echo "#### yarn.lock changed. Re-installing node_modules."
  yarn install --cwd $CD/janis
  upload_cache
fi
