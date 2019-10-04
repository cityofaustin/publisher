#!/usr/bin/env bash
set -o errexit
CD=`dirname $BASH_SOURCE`

export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}
export JANIS_BRANCH="master"
export DEST="everywhere"

touch $CD/start-build.json
pipenv run python $CD/construct_start_build_json.py
aws codebuild start-build --cli-input-json file://$CD/start-build.json
rm $CD/start-build.json # clean up artifact from construct_start_build_json.py
