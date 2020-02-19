import os, boto3, json, sys
from boto3.dynamodb.conditions import Attr
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from helpers.process_build_failure import process_build_failure
import helpers.stages as stages
from helpers.utils import get_lambda_cloudwatch_url, get_current_build_item


def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    # Get janis_branch from CodeBuild result
    codebuild_data = json.loads(event["Records"][0]["Sns"]['Message'])['detail']
    for env_var in codebuild_data['additional-information']['environment']['environment-variables']:
        if (env_var['name'] == 'JANIS_BRANCH'):
            janis_branch = env_var['value']
            break

    build_item = get_current_build_item(janis_branch)
    if not build_item:
        return None

    # Update the logs for that BLD
    build_id = build_item["build_id"]
    build_pk = build_item["pk"]
    build_sk = build_item["sk"]
    print(f"##### janis_builder_factory stage finished for [{build_id}].")
    lambda_cloudwatch_url = get_lambda_cloudwatch_url(context)
    project_name = codebuild_data['project-name']
    stream_name = codebuild_data['additional-information']['logs']['stream-name']
    codebuild_url = f'https://console.aws.amazon.com/codesuite/codebuild/projects/{project_name}/build/{project_name}%3A{stream_name}/log?region={os.getenv("AWS_REGION")}'
    publisher_table.update_item(
        Key={
            'pk': build_pk,
            'sk': build_sk,
        },
        UpdateExpression="SET logs = list_append(if_not_exists(logs, :empty_list), :logs)",
        ExpressionAttributeValues={
            ":logs": [
                {
                    'stage': stages.janis_builder_factory,
                    'lambda_url': lambda_cloudwatch_url,
                    'codebuild_url': codebuild_url,
                }
            ],
            ":empty_list": [],
        },
        ConditionExpression=Attr('stage').eq(stages.janis_builder_factory),
    )

    build_status = codebuild_data['build-status']
    if (
        (build_status == "STOPPED") or
        (build_status == "FAILED")
    ):
        process_build_failure(janis_branch, context)
    elif (build_status == "SUCCEEDED"):
        print("##### We won.")
