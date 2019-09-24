#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`

# Deploys cloudFormation stack to create Elastic Container Service that will launch your worker images.
# Only need to do this once. But the instructions are here anyway.

# --capabilities CAPABILITY_NAMED_IAM is a flag that specifies that you want to create a new IAM Role in your stack.
aws cloudformation deploy \
  --template-file $CD/ecs_cluster.yml \
  --stack-name coa-publisher-staging \
  --capabilities CAPABILITY_NAMED_IAM
