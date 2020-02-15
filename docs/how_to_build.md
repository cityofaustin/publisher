Prereqs:
  - Install aws cli and add crendentials to your machine.
  - pipenv install

1. sh src/scripts/deploy_persistent_infrastructure.sh
  - This only needs to be run once. This contains cloudformation pieces that are used by every deployment environment.
2. sh src/scripts/deploy_codebuild_source.sh
  - This is required before building the rest of the publisher infrastructure. The CodeBuild Resource won't launch properly if there isn't a codebuild_source to draw from.
3. sh src/scripts/deploy_publisher.sh
  - This will deploy all the CloudFormation resources for a publisher's DEPLOY_ENV.
4. sh src/scripts/deploy_janis_builder_base.sh
  - This must be run after the CodeBuild Resource has been created by deploy_publisher.sh. This step builds the janis_builder_base image and updates the CodeBuild project to use it.


Your logs can be found in cloudwatch under /aws/lambda/<service>-<stage>-<function>


If you update Pipfile dependencies.
1. `pipenv lock -r > src/handlers/requirements.txt` to update the requirements that go into the lambda function for your specific handler. Root Pipfile should still exist for dev administrative tasks (like deployment) that are distinct from lambda execution. 
