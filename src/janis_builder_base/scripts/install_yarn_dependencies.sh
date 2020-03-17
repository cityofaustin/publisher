#!/usr/bin/env bash
set -e
D=`dirname $BASH_SOURCE`
janis_dir=$D/../janis
cache_dir=$D/../cache
cached_modules="$cache_dir/node_modules.tar.gz"
cached_yarn_lock="$cache_dir/yarn.lock"

function clean_up {
  if [ -f "$cached_modules" ]; then
    echo "#### Cleaning up cached node_modules"
    rm $cached_modules
  fi
  if [ -f "$cached_yarn_lock" ]; then
    echo "#### Cleaning up cached yarn.lock"
    rm $cached_yarn_lock
  fi
}
trap clean_up EXIT

function upload_cache {
  # Add compressed node_modules to cache
  tar -czf $cached_modules -C $janis_dir node_modules
  node $D/s3Upload.js $cached_modules cache/$JANIS_BRANCH/node_modules.tar.gz
  # Add janis yarn.lock to cache
  node $D/s3Upload.js $janis_dir/yarn.lock cache/$JANIS_BRANCH/yarn.lock
}

function run_yarn_install {
  yarn install --cwd $janis_dir
  upload_cache
}

# Check if a cache exists for your particular $JANIS_BRANCH
# $CACHE_EXISTS written to cache_exists.tmp by checkCacheExists.js
node $D/checkCacheExists.js "$JANIS_BRANCH"
source $D/cache_exists.tmp
SECONDS=0

# Use cached node_modules if a cache exists and the yarn.lock is unchanged.
if [[ "$CACHE_EXISTS" == "True" ]]; then
  echo "#### cache exists for branch: $JANIS_BRANCH"
  SOURCE_BRANCH=$JANIS_BRANCH
  CURRENT_BRANCH_CACHE=True
else
  # If no node_module cache exists from your branch, check if master's node_modules can be used.
  echo "#### no cache exists for branch: $JANIS_BRANCH. Trying cache for master branch."
  node $D/checkCacheExists.js "master"
  source $D/cache_exists.tmp
  if [[ "$CACHE_EXISTS" == "True" ]]; then
    echo "#### cache exists for master"
    SOURCE_BRANCH=master
    CURRENT_BRANCH_CACHE=False
  fi
fi

# If no SOURCE_BRANCH was not set (because there isn't a cache for "master")
# Then install local dependencies and upload a new cache
if [ -z $SOURCE_BRANCH ]; then
  run_yarn_install
  exit 0
fi

# Copy down cached yarn.lock
node $D/s3Download.js cache/$SOURCE_BRANCH/yarn.lock $cached_yarn_lock

if [ ! -f "$cached_yarn_lock" ]; then
  echo "#### Error: no yarn.lock file was found in /cache"
  exit 1
fi
if [ ! -f "$janis_dir/yarn.lock" ]; then
  echo "#### Error: no yarn.lock file was found in /janis"
  exit 1
fi

# Check difference between cached yarn.lock and your branch's yarn.lock
# Must remove error catching because diff returns exit code 1 when there is a diff
set +e
yarn_lock_diff=$(diff <(md5sum $cached_yarn_lock | awk '{ print $1 }') <(md5sum $janis_dir/yarn.lock | awk '{ print $1 }'))
set -e

# If there is no difference between the cached yarn.lock and our janis's yarn.lock,
# Then we can use the cached node_modules
if [ "$yarn_lock_diff" = "" ]; then
  echo "#### yarn.lock unchanged. Downloading cached node_modules."
  node $D/s3Download.js cache/$SOURCE_BRANCH/node_modules.tar.gz $cached_modules
  tar -xzf $cached_modules -C $janis_dir

  # If we sourced node_modules from master, then instate a new cache for our specific branch
  if [ "$CURRENT_BRANCH_CACHE" = "False" ]; then
    upload_cache
  fi
else
  echo "#### yarn.lock changed. Re-installing node_modules."
  run_yarn_install
fi
duration=$SECONDS
echo "##### Dependencies installed in $(($duration / 60)):$(($duration % 60))"
