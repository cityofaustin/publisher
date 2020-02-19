import os, boto3, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from helpers.get_datetime import get_datetime


def handler(event, context):
    data = json.loads(event)["body"]
    dynamodb = boto3.resource('dynamodb')
    publisher_table = dynamodb.Table(f'coa_publisher_{os.getenv("DEPLOY_ENV")}')

    timestamp = get_datetime()

    # Throw errors if you're missing data

    publisher_table.put_item(
        Item={
            'pk': f'REQ#{data["janis"]}',
            'sk': timestamp,
            'status': f'waiting#{timestamp}',
            'page_ids': data["page_ids"],
            'joplin': data["joplin"],
            'env_vars': data["env_vars"],
            'build_type': data["build_type"],
        }
    )

    # return request_id
