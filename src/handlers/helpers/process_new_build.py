import os, boto3
from boto3.dynamodb.conditions import Attr

from helpers.utils import get_datetime, parse_build_id, get_current_build_item
import helpers.stages as stages


def process_new_build(janis_branch, context):
    print(f'##### New build request submitted for [{janis_branch}].')
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    # Get BLD data
    build_item = get_current_build_item(janis_branch)
    if not build_item:
        return None
    build_id = build_item["build_id"]
    build_pk = build_item["pk"]
    build_sk = build_item["sk"]

    # Skip if we've alrady processed this BLD already
    build_stage = build_item["stage"]
    if build_stage != stages.preparing_to_build:
        print(f'##### Build [{build_id}] already started')
        return None

    # Start a build, based on your BLD's build_type
    build_type = build_item["build_type"]
    if build_type == "rebuild":
        # Update the build status
        publisher_table.update_item(
            Key={
                'pk': build_pk,
                'sk': build_sk,
            },
            UpdateExpression="SET stage = :stage",
            ExpressionAttributeValues={
                ":stage": stages.janis_builder_factory,
            },
            ConditionExpression=Attr('stage').eq(stages.preparing_to_build),
        )
        # Start CodeBuild Project
        codebuild = boto3.client('codebuild')

        res = codebuild.start_build(
            projectName=f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}',
            environmentVariablesOverride=[
                {
                    "name": "JANIS_BRANCH",
                    "value": janis_branch,
                    "type": "PLAINTEXT"
                },
                {
                    "name": "DEST",
                    "value": "placeholder!",
                    "type": "PLAINTEXT",
                },
                {
                    "name": "build_id",
                    "value": build_id,
                    "type": "PLAINTEXT",
                }
            ],
        )
        print(f"##### Starting janis_builder_factory for [{build_id}]")
    else:
        print("##### skipping for now.")
        # We need to run task
