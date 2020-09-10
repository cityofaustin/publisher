#!/usr/bin/env bash
set -a
D=`dirname $BASH_SOURCE`
PREV_D=$(pwd)
source $D/../../.env # Source environment variables
sh $D/../utils/check_mandatory_vars.sh

function clean_up {
  cd $PREV_D
}
trap clean_up EXIT

# sls commands must be run from directory where your serverless.yml template lives
SLS_D=$D/../..
cd $SLS_D

sls deploy --conceal $@
