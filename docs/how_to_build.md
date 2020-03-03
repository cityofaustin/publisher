Prereqs:
  - Install aws cli and add crendentials to your machine.
  - pipenv install

1. sh src/scripts/deploy_persistent_infrastructure.sh
  - This only needs to be run once. This contains cloudformation pieces that are used by every deployment environment.
2. sh src/scripts/deploy_codebuild_source.sh
  - This is required before building the rest of the publisher infrastructure (the first time). The CodeBuild Resource won't launch properly if there isn't a codebuild_source to draw from.
3. sh src/scripts/deploy_publisher.sh
  - This will deploy all the CloudFormation resources for a publisher's DEPLOY_ENV.
4. sh src/scripts/deploy_janis_builder_base.sh
  - This must be run after the CodeBuild Resource has been created by deploy_publisher.sh. This step builds the janis_builder_base image and updates the CodeBuild project to use it.
  - You'll need to run a build_type="rebuild" to create a janis_builder image that's built off your newest janis_builder_base image.


Your logs can be found in cloudwatch under /aws/lambda/<service>-<stage>-<function>


If you update Pipfile dependencies.
1. `pipenv lock -r > src/handlers/requirements.txt` to update the requirements that go into the lambda function for your specific handler. Root Pipfile should still exist for dev administrative tasks (like deployment) that are distinct from lambda execution.


Adding support for additional environment variables:
For a "rebuild" build_type:
1. handlers/helpers.utils.get_janis_builder_factory_env_vars
2. janis_builder_factory_source/buildspec.yml pass in as build-arg
3. janis_builder_factory_source/janis-builder.Dockerfile to receive env_vars within image
  - Remember to scripts/deploy_codebuild_source.sh to push those changes!
4. handlers/helpers/valid_optional_env_vars if it's an optional environment variable passed in with a publish_request's "env_vars" param
Then for other build_types:
1. handlers/commands/run_janis_builder_task
