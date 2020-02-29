import os, boto3, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from commands.process_build_failure import process_build_failure
from helpers.utils import get_lambda_cloudwatch_url, parse_build_id, get_janis_branch


def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    fargate_data = json.loads(event["Records"][0]["Sns"]['Message'])['detail']
    print("##### hi")
    print(fargate_data)
    for env_var in fargate_data['additional-information']['environment']['environment-variables']:
        if (env_var['name'] == 'BUILD_ID'):
            build_id = env_var['value']
            break

    print(f"##### janis_builder_factory stage finished for [{build_id}].")
    try:
        print("##### it didn't explode")
    except Exception as error:
        print(error)
        janis_branch = get_janis_branch(build_id)
        process_build_failure(janis_branch, context)
