import os, json, boto3

ecs_client = boto3.client('ecs')
s3_client = boto3.client('s3')

register_response = ecs_client.register_task_definition(
   containerDefinitions=[
      {
         "image": f'cityofaustin/janis-builder:{os.getenv("JANIS_BRANCH")}',
         "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
               "awslogs-group" : "/ecs/fargate-task-definition",
               "awslogs-region": "us-east-1",
               "awslogs-stream-prefix": "ecs"
            }
         },
         "cpu": 1024,
         "memory": 2048,
         "name": f'janis-builder-{os.getenv("JANIS_BRANCH")}',
      }
   ],
   cpu="1024",
   memory="2048",
   executionRoleArn=f'arn:aws:iam::{os.getenv("AWS_ACCOUNT_ID")}:role/coa-publisher-task-execution',
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
    Body=register_response['taskDefinition']['taskDefinitionArn'].encode('utf-8')
)
