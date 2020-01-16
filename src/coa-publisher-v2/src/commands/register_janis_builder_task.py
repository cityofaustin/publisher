import os, json, boto3

# After you've created your janis_builder image
# you must register it as a Fargate task.
# Then you can execute that task in order to run your janis_builder container.
def register_janis_builder_task(janis_branch):
    ecs_client = boto3.client('ecs')
    s3_client = boto3.client('s3')
    cf_client = boto3.client('cloudformation')

    # Get the executionRoleArn from your CloudFormation stack outputs
    cf_outputs = cf_client.describe_stacks(
        StackName=f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "ECSTaskExecutionRole":
            executionRoleArn = x["OutputValue"]
    if not executionRoleArn:
        raise Exception(f"No ECSTaskExecutionRole found in coa-publisher-{os.getenv('DEPLOY_ENV')} stack")

    # Get the janis_builder_ecr_uri from your CloudFormation stack outputs
    cf_outputs = cf_client.describe_stacks(
        StackName=f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}'
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "JanisBuilderEcrUri":
            janis_builder_ecr_uri = x["OutputValue"]
    if not janis_builder_ecr_uri:
        raise Exception(f"No JanisBuilderEcrUri found in coa-publisher-janis-builder-factory-{os.getenv('DEPLOY_ENV')} stack")
    janis_builder_image = f"{janis_builder_ecr_uri}:{janis_branch}-latest"

    # Register task definition for ECS to launch janis-builder:$JANIS_BRANCH containers
    print(f"Registering Fargate task `janis-builder-{janis_branch}`")
    register_res = ecs_client.register_task_definition(
       containerDefinitions=[
          {
             "image": janis_builder_image,
             "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                   "awslogs-group" : "/coa-publisher/janis-builder",
                   "awslogs-region": "us-east-1",
                   "awslogs-stream-prefix": janis_branch
                }
             },
             "cpu": 1024,
             "memory": 2048,
             "name": f'janis-builder-{janis_branch}',
          }
       ],
       cpu="1024",
       memory="2048",
       executionRoleArn=executionRoleArn,
       family=f'janis-builder-{janis_branch}',
       networkMode="awsvpc",
       requiresCompatibilities=[
           "FARGATE"
       ]
    )
