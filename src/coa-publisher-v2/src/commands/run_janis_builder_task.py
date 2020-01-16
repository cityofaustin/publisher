import os, json, boto3
from helpers.naming import github_to_aws

def run_janis_builder_task(janis_branch):
    ecs_client = boto3.client('ecs')
    s3_client = boto3.client('s3')
    cf_client = boto3.client('cloudformation')
    janis_branch = os.getenv("JANIS_BRANCH")
    sanitized_janis_branch = github_to_aws(janis_branch)

    # Retrieve latest task definition ARN (with revision number)
    latest_task_definition = ecs_client.list_task_definitions(
        familyPrefix=f'janis-builder-{sanitized_janis_branch}',
        sort="DESC",
        maxResults=1,
    )['taskDefinitionArns'][0]

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
    print("About to run the task")
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
                    'name': f'janis-builder-{sanitized_janis_branch}',
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
