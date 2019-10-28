#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`
PREV_CD=$(pwd)

function clean_up {
  cd $PREV_CD
}
trap clean_up EXIT

# sets src/coa-publisher-mvp as your current directory
# necessary because "pipenv run zappa" wants zappa_settings to be at the "root" of your project directory.
cd $CD/..

pipenv run zappa tail
