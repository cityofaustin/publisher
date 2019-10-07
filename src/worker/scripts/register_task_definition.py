import os, json, boto3

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

# Register task definition for ECS to launch janis-builder:$JANIS_BRANCH containers
register_res = ecs_client.register_task_definition(
   containerDefinitions=[
      {
         "image": f'cityofaustin/janis-builder:{os.getenv("JANIS_BRANCH")}',
         "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
               "awslogs-group" : "/coa-publisher/janis-builder",
               "awslogs-region": "us-east-1",
               "awslogs-stream-prefix": f'{os.getenv("JANIS_BRANCH")}'
            }
         },
         "cpu": 1024,
         "memory": 2048,
         "name": f'janis-builder-{os.getenv("JANIS_BRANCH")}',
      }
   ],
   cpu="1024",
   memory="2048",
   executionRoleArn=executionRoleArn,
   family=f'janis-builder-{os.getenv("JANIS_BRANCH")}',
   networkMode="awsvpc",
   requiresCompatibilities=[
       "FARGATE"
   ]
)

# Store latest task definition ARN (with revision number) to use later
s3_client.put_object(
    Bucket='coa-publisher',
    Key=f'cache/{os.getenv("JANIS_BRANCH")}/latest_task_definition.txt',
    Body=register_res['taskDefinition']['taskDefinitionArn'].encode('utf-8')
)
