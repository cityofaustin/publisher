import os, boto3, json

from helpers.utils import get_cms_api_url, parse_build_id, get_janis_branch
import helpers.stages as stages


def run_janis_builder_task(build_item, latest_task_definition):
    ecs_client = boto3.client('ecs')
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)
    build_id = build_item['build_id']
    build_pk, build_sk = parse_build_id(build_id)
    janis_branch = get_janis_branch(build_id)

    # Start the Task
    print(f'##### Running janis_builder task for [{build_id}]')

    task_env_vars = [
        {
            'name': 'BUILD_TYPE',
            'value': build_item['build_type'],
        },
        {
            'name': 'CMS_API',
            'value': get_cms_api_url(build_item['joplin']),
        },
        {
            'name': 'PAGE_IDS',
            'value': json.dumps([str(page_id) for page_id in build_item["page_ids"]]),
        },
        {
            'name': 'BUILD_ID',
            'value': build_id,
        }
    ]

    for name, value in build_item["env_vars"].items():
        task_env_vars.append({
            'name': name,
            'value': value
        })

    task = ecs_client.run_task(
        cluster=os.getenv("ECS_CLUSTER"),
        taskDefinition=latest_task_definition,
        launchType='FARGATE',
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [
                    os.getenv("PUBLIC_SUBNET_ONE"),
                    os.getenv("PUBLIC_SUBNET_TWO"),
                ],
                "securityGroups": [
                    os.getenv("CLUSTER_SECURITY_GROUP"),
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': f'janis-builder-{janis_branch}',
                    'environment': task_env_vars,
                }
            ]
        },
    )

    # Update the logs for your BLD
    task_id = (task['tasks'][0]['taskArn']).split('task/')[1]
    publisher_table.update_item(
        Key={
            'pk': build_pk,
            'sk': build_sk,
        },
        UpdateExpression="SET stage = :stage, logs = list_append(if_not_exists(logs, :empty_list), :logs)",
        ExpressionAttributeValues={
            ":stage": stages.run_janis_builder_task,
            ":logs": [
                {
                    'stage': stages.run_janis_builder_task,
                    'url': f'https://console.aws.amazon.com/ecs/home?region={os.getenv("AWS_REGION")}#/clusters/{os.getenv("ECS_CLUSTER")}/tasks/{task_id}/details',
                }
            ],
            ":empty_list": [],
        },
    )
