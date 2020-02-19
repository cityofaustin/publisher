import os, boto3, json, sys
from boto3.dynamodb.conditions import Attr
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from helpers.process_build_failure import process_build_failure
import helpers.stages as stages
from helpers.get_lambda_cloudwatch_url import get_lambda_cloudwatch_url


def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    # Get janis_branch from CodeBuild result
    build_data = json.loads(event["Records"][0]["Sns"]['Message'])['detail']
    for env_var in build_data['additional-information']['environment']['environment-variables']:
        if (env_var['name'] == 'JANIS_BRANCH'):
            janis_branch = env_var['value']
            break

    # Get currently "building" BLD for janis_branch
    build_pk = f'BLD#{janis_branch}'
    build_item = publisher_table.get_item(
        Key={
            'pk': build_pk,
            'sk': 'building',
        },
        ProjectionExpression='build_id',
    )
    if not 'Item' in build_item:
        print(f"##### No 'building' BLD found for {build_pk}.")
        return None

    # Update the logs for that BLD
    print(f"##### janis_builder_factory stage finished for {build_item['Item']['build_id']}")
    lambda_cloudwatch_url = get_lambda_cloudwatch_url(context)
    project_name = build_data['project-name']
    stream_name = build_data['additional-information']['logs']['stream-name']
    codebuild_url = f'https://console.aws.amazon.com/codesuite/codebuild/projects/{project_name}/build/{project_name}%3A{stream_name}/log?region={os.getenv("AWS_REGION")}'
    publisher_table.update_item(
        Key={
            'pk': build_pk,
            'sk': 'building',
        },
        UpdateExpression="SET logs = list_append(logs, :logs)",
        ExpressionAttributeValues={
            ":logs": [
                {
                    'stage': stages.janis_builder_factory,
                    'lambda_url': lambda_cloudwatch_url,
                    'codebuild_url': codebuild_url,
                }
            ],
        },
        ConditionExpression=Attr('stage').eq(stages.janis_builder_factory),
    )

    build_status = build_data['build-status']
    if (
        (build_status == "STOPPED") or
        (build_status == "FAILED")
    ):
        process_build_failure(janis_branch, context)
    elif (build_status == "SUCCEEDED"):
        print("##### We won.")
