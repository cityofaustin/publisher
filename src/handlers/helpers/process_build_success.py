import os, boto3, json
from boto3.dynamodb.conditions import Key
import dateutil.parser

from helpers.get_datetime import get_datetime


def process_build_success(janis_branch, context):
    client = boto3.client('dynamodb')
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
    )
    if not 'Item' in build_item:
        print("Successful build has already been handled")
        return None

    build_config = build_item["Item"]
    start_build_time = dateutil.parser.parse(build_config["build_id"].split('#')[2])
    end_build_time = dateutil.parser.parse(timestamp)
    total_build_time = str(end_build_time - start_build_time)

    write_item_batch = []
    # Delete the old "building" build_item
    deleted_build_item = {
        "Delete": {
            "TableName": table_name,
            "Key": {
                "pk": {'S': build_pk},
                "sk": {'S': "building"},
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    # Create a new build_item that has all of the same properties as the original build_item
    # But resets the "sk" from "building" to "succeeded#{timestamp}".
    # Adds "total_build_time"
    new_build_item = {
        "Put": {
            "TableName": table_name,
            "Item": {
                "pk": {'S': build_pk},
                "sk": {'S': f"succeeded#{timestamp}"},
                "build_id": {'S': build_config["build_id"]},
                "build_type": {'S': build_config["build_type"]},
                "joplin": {'S': build_config["joplin"]},
                "page_ids": {'L': [{'N': str(page_id)} for page_id in build_config["page_ids"]]},
                "env_vars": {'M': {'S': env_var for env_var in build_config["env_vars"]}},
                "total_build_time": {'S': total_build_time},
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(deleted_build_item)
    write_item_batch.append(new_build_item)
    client.transact_write_items(TransactItems=write_item_batch)
