#!/usr/bin/env bash
D=`dirname $BASH_SOURCE`
source $D/../../.env
export DEPLOY_ENV=${DEPLOY_ENV:-"staging"}

if [ "$DEPLOY_ENV" != "staging" ] && [ "$DEPLOY_ENV" != "prod" ]; then
  echo "Error: DEPLOY_ENV must be set to 'staging' or 'prod'."
  exit 1
fi

# Build coa-publisher cloudformation stack
# Only need to do this once. But the instructions are here anyway.
# --capabilities CAPABILITY_NAMED_IAM is a flag that specifies that you want to create a new IAM Role in your stack.
aws cloudformation deploy \
  --template-file $D/template.yml \
  --parameter-overrides \
    Env="$DEPLOY_ENV" \
    RdsMasterUsername="$RDS_MASTER_USERNAME" \
    RdsMasterPw="$RDS_MASTER_PW" \
  --stack-name coa-publisher-$DEPLOY_ENV \
  --capabilities CAPABILITY_NAMED_IAM \
  --tags user:app=publisher user:stage=$DEPLOY_ENV user:project=alpha.austin.gov
