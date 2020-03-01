import os, boto3

# After you've created your janis_builder image, you must register it as a Fargate task.
# Then you can execute that task in order to run your janis_builder container.
def register_janis_builder_task(janis_branch):
    ecs_client = boto3.client('ecs')

    # This is the image tag assigned in codebuild.yml
    janis_builder_image = f'{os.getenv("JANIS_BUILDER_ECR_URI")}:{janis_branch}-latest'

    # Register task definition for ECS to launch janis-builder:$JANIS_BRANCH containers
    print(f'##### janis-builder-factory successful. We now have a new janis-builder image for [{janis_branch}]')
    print(f"##### Now registering the Fargate task for [janis-builder-{janis_branch}]")
    ecs_client.register_task_definition(
       containerDefinitions=[
          {
             "image": janis_builder_image,
             "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    # As specified by JanisBuilderLogGroup
                   "awslogs-group" : f'/coa-publisher-{os.getenv("DEPLOY_ENV")}/janis-builder',
                   "awslogs-region": os.getenv("AWS_REGION"),
                   "awslogs-stream-prefix": janis_branch,
                }
             },
             "cpu": 1024,
             "memory": 2048,
             "name": f'janis-builder-{janis_branch}',
          }
       ],
       cpu="1024",
       memory="2048",
       executionRoleArn=os.getenv("JANIS_BUILDER_TASK_EXECUTION_ROLE"),
       taskRoleArn=os.getenv("JANIS_BUILDER_ROLE"),
       family=f'janis-builder-{janis_branch}',
       networkMode="awsvpc", # required for Fargate launch types
       requiresCompatibilities=[
           "FARGATE"
       ]
    )
