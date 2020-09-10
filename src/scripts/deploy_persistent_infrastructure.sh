#!/usr/bin/env bash
set -a
D=`dirname $BASH_SOURCE`
sh $D/../utils/check_mandatory_vars.sh

aws cloudformation deploy \
  --template-file $D/../templates/persistent.yml \
  --stack-name coa-publisher-persistent-infrastructure \
  --capabilities CAPABILITY_NAMED_IAM \
  --tags user:app=publisher user:stage=prod user:project=alpha.austin.gov
