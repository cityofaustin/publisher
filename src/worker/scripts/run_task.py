import os, json, boto3

ecs_client = boto3.client('ecs')
s3_client = boto3.client('s3')
cf_client = boto3.client('cloudformation')

# Retrieve latest task definition ARN (with revision number)
latest_task_definition = s3_client.get_object(
    Bucket='coa-publisher',
    Key=f'cache/{os.getenv("JANIS_BRANCH")}/latest_task_definition.txt'
)['Body'].read().decode('utf-8')

# Retrieve the subnets to use from your CloudFormation Stack
cf_outputs = cf_client.describe_stacks(
    StackName=f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
)['Stacks'][0]['Outputs']

for x in cf_outputs:
    if x['OutputKey'] == "PublicSubnetOne":
        PublicSubnetOne = x['OutputValue']
    elif x['OutputKey'] == "PublicSubnetTwo":
        PublicSubnetTwo = x['OutputValue']

# Start the Task
ecs_client.run_task(
    cluster='coa-publisher',
    taskDefinition=latest_task_definition,
    launchType='FARGATE',
    networkConfiguration={
        "awsvpcConfiguration": {
            "subnets": [
                PublicSubnetOne,
                PublicSubnetTwo,
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    overrides={
        'containerOverrides': [
            {
                'name': f'janis-builder-{os.getenv("JANIS_BRANCH")}',
                'environment': [
                    {
                        'name': 'DEST',
                        'value': 'outer space'
                    },
                    {
                        'name': 'JANIS_BRANCH',
                        'value': 'tomorrow'
                    }
                ]
            }
        ]
    },
)
