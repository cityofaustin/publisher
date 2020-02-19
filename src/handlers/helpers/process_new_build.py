import os, boto3, json
from boto3.dynamodb.conditions import Attr

from helpers.get_datetime import get_datetime
import helpers.stages as stages


def process_new_build(janis_branch, context):
    print("##### New build request submitted.")
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    build_pk = f'BLD#{janis_branch}'
    timestamp = get_datetime()
    build_item = publisher_table.get_item(
        Key={
            'pk': build_pk,
            'sk': 'building',
        },
        ProjectionExpression='pk, sk, stage, build_id, build_type',
    )
    if not 'Item' in build_item:
        print(f'##### No "building" BLD found for {build_pk}.')
        return None

    build_stage = build_item["Item"]["stage"]
    if build_stage != stages.preparing_to_build:
        print(f'##### Build {build_item["Item"]["build_id"]} already started')
        return None

    build_type = build_item["Item"]["build_type"]
    if build_type == "rebuild":
        # Update the build status
        publisher_table.update_item(
            Key={
                'pk': build_pk,
                'sk': 'building',
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
            ],
        )
        print(f"##### Starting janis_builder_factory for {build_pk}")
    else:
        print("##### skipping for now.")
        # We need to run task
