#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`
PREV_CD=$(pwd)

function clean_up {
  cd $PREV_CD
}
trap clean_up EXIT

# set src/coa-publisher-basic as your current directory
# necessary because "pipenv run zappa" wants zappa_settings to be at the "root" of your project directory.
cd $CD/..

# Dynamically construct the zappa settings for our app
pipenv run python ./deploy/build_zappa_settings.py

echo "########"
echo "zappa_settings.json:"
echo "########"
cat ./zappa_settings.json

# Check if lambda function already exists.
# set +e temporarily allows us to throw errors.
# If `get-function` returns a 255 error, then we know that our lambda does not exist and needs to be deployed.
set +e
ZAPPA_FUNCTION=$(echo "coa-publisher-basic-pr" | sed 's/_/-/g')
$(aws lambda get-function --function-name $ZAPPA_FUNCTION > /dev/null)
result=$?
set -e
if [ "$result" == 0 ]; then
  # Update zappa lambda if it exists
  pipenv run zappa update pr
else
  # Deploy new lambda function if it doesn't exist
  pipenv run zappa deploy pr
fi
