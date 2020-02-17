import os, boto3, json
from boto3.dynamodb.conditions import Attr

from .get_datetime import get_datetime


def process_new_build(janis_branch):
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
        ProjectionExpression='pk, sk, #s, build_type',
        ExpressionAttributeNames={ "#s": "status" },
    )
    if not 'Item' in build_item:
        print(f"##### No 'building' BLD found for {build_pk}.")
        return None

    build_status = build_item["Item"]["status"]
    preparing_to_start_status = "preparing_to_start"
    if build_status != preparing_to_start_status:
        print(f"##### Build {build_pk} already started")
        return None

    build_type = build_item["Item"]["build_type"]
    if build_type == "rebuild":
        # Update the build status
        publisher_table.update_item(
            Key={
                'pk': build_pk,
                'sk': 'building',
            },
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={ "#s": "status" },
            ExpressionAttributeValues={
                ":status": "janis_builder_factory"
            },
            ConditionExpression=Attr('status').eq(preparing_to_start_status),
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
        print(res)
    else:
        print("##### skipping for now.")
        # We need to run task
