#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`

cached_modules="$CD/cache/node_modules.tar.gz"
cached_yarn_lock="$CD/cache/yarn.lock"

# Use cached node_modules if a cache exists and the yarn.lock is unchanged.
if [[ $(python $CD/cache_exists.py) == "True" ]]; then
  aws s3 cp s3://coa-publisher/cache/$JANIS_BRANCH/yarn.lock $cached_yarn_lock
  echo "~~~ What is here?"
  ls -la
  ls -la ./cache
  yarn_lock_diff=$(diff <(md5sum $cached_yarn_lock) <(md5sum $CD/janis/yarn.lock))
  if [ "$yarn_lock_diff" = "" ]; then
    echo "yarn.lock unchanged. Using cached node_modules/"
    aws s3 cp s3://coa-publishe/cache/$JANIS_BRANCH/node_modules.tar.gz $cached_modules
    tar -xzvf $cached_modules -C $CD/janis
    rm $cached_modules
    exit 0
  fi
fi

# Install node_modules and add them to the cache
yarn install --cwd $CD/janis
# Add compressed node_modules to cache
tar -czf $cached_modules -C janis $CD/node_modules
aws s3 cp $cached_modules s3://coa-publisher/cache/$JANIS_BRANCH/node_modules.tar.gz
rm $cached_modules
# Add yarn.lock to cache
aws s3 cp $CD/janis/yarn.lock s3://coa-publisher/cache/$JANIS_BRANCH/yarn.lock
