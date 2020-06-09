# How to Build

The Publisher entirely consists of AWS resources, therefore there is no way to run it locally.

However, you can create your own PR/Test environment in AWS.

## Things you need to install:
1. Install aws cli and add crendentials to your machine.
2. Install the Serverless Framework `npm install -g serverless`/`npm update -g serverless`. https://serverless.com/framework/docs/getting-started/
3. Install the helper packages for Serverless `yarn install`.
4. Install python dependencies with `pipenv install`
5. Add a .env file and fill it out your own credentials `cp .template.env .env`.

## How test environments work
The .env file is very important. The DEPLOY_ENV you set in .env will create/update whichever stack you set. Every deployment script in `/src/scripts/` will read from .env to determine which environment they will update.
  - If you set `DEPLOY_ENV=production`, then running your scripts will update production.
  - If you set `DEPLOY_ENV=staging`, then running your scripts will update staging.
  - If you set `DEPLOY_ENV=myTestPublisher`, for example, then running your scripts will create a new Publisher stack called "myTestPublisher". Every single piece of the Publisher will be recreated for your test Publisher (with the exception of Resources in src/templates/persistent.yml, which are shared by all environments). You can safely Publish to "myTestPublisher" without the threat of impacting staging or production. This is how we'll test and develop new features for the Publisher.

When creating a test Publisher please adhere to these conventions:
1. Name your publisher using the same style that we use for naming branches. [Issue Number]-[short description]. Ex: 1234-update-logging
2. Please delete your test stack when you're done using it.

## How to Deploy
We have 4 scripts used to deploy the Publisher. Not all 4 of them should be run for every type of update. It seems like a lot, but it'll all come together, trust me. We have 4 scripts instead of 1 or 2 because CodeBuild has some finicky steps in order to make it work, which you will soon read about.

1. sh src/scripts/deploy_persistent_infrastructure.sh
  - This only needs to be run once. Once, period. Not once for each DEPLOY_ENV, once for every DEPLOY_ENV. This contains cloudformation pieces that are used by every DEPLOY_ENV (src/templates/persistent.yml). The one S3 Bucket, the one ECR repo where we stole docker images for all environments.
  - We'd only have to run this script again if we were rebuilding everything from scratch on a new environment.
  - It's good to know what this does, but in all likelihood, you won't need to use it.

2. sh src/scripts/deploy_codebuild_source.sh
  - This must be done for each DEPLOY_ENV.
  - Before we build out all the AWS Resources for Publisher in step (3), we need to put the build instructions for janis_builder_factory's CodeBuild project in our S3 Bucket.
  - Why do we need to do this first before building everything else? Because the CodeBuild Resource won't launch properly if there isn't a codebuild_source to draw from.
  - When do I need to re-run this step? If you make any changes to the files in `src/janis_builder_factory_source/*`:
    - `janis-builder.Dockerfile`
    - `buildspec.yml`

3. sh src/scripts/deploy_publisher.sh
  - This must be done for each DEPLOY_ENV.
  - This will update/deploy all the AWS resources for a publisher's DEPLOY_ENV. This step makes everything.
  - We build our lambda functions and AWS resources using the Serverless Framework. If you want to do optional fancy things, you can pass in any of the flags that you'd use for `sls deploy` into `src/scripts/deploy_publisher.sh`. Ex: `sh src/scripts/deploy_publisher.sh -f myFunction`.
  - When do I need to re-run this step? If you change anything in:
    1. The `serverless.yml` file that brings everything together.
    2. Your AWS templates `src/templates/*`
    3. Your python code in `src/handlers/*`

4. sh src/scripts/deploy_janis_builder_base.sh
  - This must be done for each DEPLOY_ENV.
  - This step builds the janis_builder_base image and updates the CodeBuild project to use it.
  - This must be run after the CodeBuild Resource has been created by deploy_publisher.sh in step (3).
  - You'll need to run a build_type="rebuild" in order to create a janis_builder image that's built off your newest janis_builder_base image.
  - When do I need to re-run this step? Whenever you update anything that goes into your janis_builder_base `src/janis_builder_base/`. Again, you'll then have to do a publish with build_type="rebuild" in order for your janis_builder image to be created with your updated "janis_builder_base".

## If you update Pipfile dependencies
`pipenv lock -r > src/handlers/requirements.txt` to update the requirements that go into the lambda function for your specific handler. Root Pipfile should still exist for dev administrative tasks (like deployment) that are distinct from lambda execution.

## Adding support for additional environment variables
Let's say that we decide that our janis_builder build_site.sh needs access to new environment variables. There is a bit of chaining required in order to make sure those environment variables finally get into the janis_builder docker container.

For a "rebuild" build_type:
1. handlers/helpers.utils.get_janis_builder_factory_env_vars
2. janis_builder_factory_source/buildspec.yml pass in as build-arg
3. janis_builder_factory_source/janis-builder.Dockerfile to receive env_vars within image
  - Remember to run step (2) `sh scripts/deploy_codebuild_source.sh` to push those changes!
4. Add to `handlers/helpers/valid_optional_env_vars` if it's an optional environment variable that is passed in with a publish_request's "env_vars" param.


Then for "all_pages" and "incremental" build_types:
1. Add to `handlers/commands/run_janis_builder_task`
