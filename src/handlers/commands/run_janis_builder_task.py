import os, boto3


def run_janis_builder_task(janis_branch):
    print("##### Skipping for now.")
    return None
    ecs_client = boto3.client('ecs')
    s3_client = boto3.client('s3')
    cf_client = boto3.client('cloudformation')

    # Retrieve latest task definition ARN (with revision number)
    latest_task_definition = get_latest_task_definition(janis_branch)

    # Retrieve the subnets to use from your CloudFormation Stack
    cf_outputs = cf_client.describe_stacks(
        StackName=f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "PublicSubnetOne":
            PublicSubnetOne = x['OutputValue']
        elif x['OutputKey'] == "PublicSubnetTwo":
            PublicSubnetTwo = x['OutputValue']
        elif x['OutputKey'] == "ClusterSecurityGroup":
            ClusterSecurityGroup = x['OutputValue']

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
                "securityGroups": [
                    ClusterSecurityGroup,
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': f'janis-builder-{janis_branch}',
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
