import os, boto3

import helpers.stages as stages
from helpers.utils import parse_build_id, get_build_item, get_janis_builder_factory_env_vars, get_dynamodb_table


def start_janis_builder_factory(build_id):
    queue_table = get_dynamodb_table()

    build_pk, build_sk = parse_build_id(build_id)
    queue_table.update_item(
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
    )

    # Start CodeBuild Project
    codebuild = boto3.client('codebuild')
    build_item = get_build_item(build_id)
    codebuild.start_build(
        projectName=f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}',
        environmentVariablesOverride=get_janis_builder_factory_env_vars(build_item),
    )
    print(f"##### Starting janis_builder_factory for [{build_id}]")
