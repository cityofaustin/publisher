import os, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from commands.process_build_failure import process_build_failure
from commands.process_build_success import process_build_success
from helpers.utils import get_lambda_cloudwatch_url, parse_build_id, get_dynamodb_table
import helpers.stages as stages


def handler(event, context):
    queue_table = get_dynamodb_table()

    sns_detail = json.loads(event["Records"][0]["Sns"]['Message'])['detail']
    # Someday we might be listening for other tasks besides "janis-builder".
    # But for now, "family:janis-builder-{janis_branch}" is the only group of tasks we're running
    if sns_detail["group"].startswith("family:janis-builder"):
        for env_var in sns_detail["overrides"]["containerOverrides"][0]["environment"]:
            if (env_var['name'] == 'BUILD_ID'):
                build_id = env_var['value']
                break
    print(f"##### janis_builder fargate task finished for [{build_id}].")
    build_pk, build_sk = parse_build_id(build_id)
    lambda_cloudwatch_url = get_lambda_cloudwatch_url(context)
    try:
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
                        'stage': stages.final,
                        'url': lambda_cloudwatch_url,
                    }
                ],
                ":empty_list": [],
            },
        )

        exit_code = sns_detail["containers"][0]["exitCode"]
        if exit_code == 0:
            process_build_success(build_id, context)
        else:
            print(f"##### Failure: janis_builder exited with nonzero exit code for [{build_id}].")
            process_build_failure(build_id, context)
    except Exception as error:
        import traceback
        print(traceback.format_exc())
        process_build_failure(build_id, context)
