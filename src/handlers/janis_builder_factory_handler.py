import os, json, sys
from boto3.dynamodb.conditions import Attr
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from commands.process_build_failure import process_build_failure
from commands.register_janis_builder_task import register_janis_builder_task
from commands.process_build_success import process_build_success
from commands.process_build_failure import process_build_failure
import helpers.stages as stages
from helpers.utils import get_lambda_cloudwatch_url, parse_build_id, get_janis_branch, get_dynamodb_table


def handler(event, context):
    queue_table = get_dynamodb_table()

    sns_detail = json.loads(event["Records"][0]["Sns"]['Message'])['detail']
    for env_var in sns_detail['additional-information']['environment']['environment-variables']:
        if (env_var['name'] == 'BUILD_ID'):
            build_id = env_var['value']
            break
    build_pk, build_sk = parse_build_id(build_id)
    janis_branch = get_janis_branch(build_id)
    print(f"##### janis_builder_factory stage finished for [{build_id}].")
    try:
        # Update the logs for that BLD
        lambda_cloudwatch_url = get_lambda_cloudwatch_url(context)
        project_name = sns_detail['project-name']
        stream_name = sns_detail['additional-information']['logs']['stream-name']
        codebuild_url = f'https://console.aws.amazon.com/codesuite/codebuild/projects/{project_name}/build/{project_name}%3A{stream_name}/log?region={os.getenv("AWS_REGION")}'
        queue_table.update_item(
            Key={
                'pk': build_pk,
                'sk': build_sk,
            },
            UpdateExpression="SET stage = :stage, logs = list_append(if_not_exists(logs, :empty_list), :logs)",
            ExpressionAttributeValues={
                ":stage": stages.final,
                ":logs": [
                    {
                        'stage': stages.janis_builder_factory,
                        'url': codebuild_url,
                    },
                    {
                        'stage': stages.final,
                        'url': lambda_cloudwatch_url,
                    }
                ],
                ":empty_list": [],
            },
        )

        build_status = sns_detail['build-status']
        if (
            (build_status == "STOPPED") or
            (build_status == "FAILED")
        ):
            print(f"##### Failure: janis_builder_factory did not succeed for [{build_id}].")
            process_build_failure(build_id, context)
        elif (build_status == "SUCCEEDED"):
            register_janis_builder_task(janis_branch)
            process_build_success(build_id, context)
    except Exception as error:
        import traceback
        print(traceback.format_exc())
        process_build_failure(build_id, context)
