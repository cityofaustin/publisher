#!/usr/bin/env bash
set -a
D=`dirname $BASH_SOURCE`
PREV_D=$(pwd)

function clean_up {
  cd $PREV_D
}
trap clean_up EXIT

# sls commands must be run from directory where your serverless.yml template lives
SLS_D=$D/../templates
cd $SLS_D

AWS_REGION=us-east-1
SLS_STAGE=test
sls deploy --config
