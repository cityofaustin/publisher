import os, boto3
from boto3.dynamodb.conditions import Attr

import helpers.stages as stages
from helpers.utils import parse_build_id, get_current_build_item, get_janis_builder_factory_env_vars


def start_janis_builder_factory(build_id):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    build_pk, build_sk = parse_build_id(build_id)
    janis_branch = build_pk.split('#')[1]
    publisher_table.update_item(
        Key={
            'pk': build_pk,
            'sk': build_sk,
        },
        UpdateExpression="SET stage = :stage, build_type = :build_type",
        ExpressionAttributeValues={
            ":stage": stages.janis_builder_factory,
            # ensure that build_type=rebuild.
            # If an "incremental" or "all_pages" BLD did find a janis_builder_task to run, then a "rebuild" is necessary
            ':build_type': "rebuild",
        },
        ConditionExpression=Attr('stage').eq(stages.preparing_to_build),
    )

    # Start CodeBuild Project
    codebuild = boto3.client('codebuild')
    build_item = get_current_build_item(janis_branch)
    codebuild.start_build(
        projectName=f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}',
        environmentVariablesOverride=get_janis_builder_factory_env_vars(janis_branch, build_item),
    )
    print(f"##### Starting janis_builder_factory for [{build_id}]")
