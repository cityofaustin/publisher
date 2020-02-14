import os, boto3, json
from boto3.dynamodb.conditions import Key

from .helpers.get_datetime import get_datetime

table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'


def build_failure_handler(event, context):
    data = json.loads(event)["body"]
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    publisher_table = dynamodb.Table(table_name)

    janis_branch = data["janis"]
    build_pk = f'BLD#{janis_branch}'
    timestamp = get_datetime()

    build_item = publisher_table.get_item(
        Key={
            'pk': build_pk,
            'sk': 'building',
        },
    )
    if not 'Item' in build_item:
        print("Failed build has already been handled")
        return None

    build_id = build_item["Item"]["build_id"]
    req_pk = f'REQ#{janis_branch}'
    assinged_reqs = publisher_table.query(
        IndexName="build_id.janis",
        Select='ALL_ATTRIBUTES',
        ScanIndexForward=True,
        KeyConditionExpression= Key('build_id').eq(build_id) & Key('pk').eq(req_pk)
    )['Items']

    write_item_batches = []
    write_item_batch = []
    # Delete the failed build_item
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
    # But resets the "sk" from "building" to "failed#{timestamp}"
    build_config = build_item["Item"]
    new_build_item = {
        "Put": {
            "TableName": table_name,
            "Item": {
                "pk": {'S': build_pk},
                "sk": {'S': f"failed#{timestamp}"},
                "build_id": {'S': build_config["build_id"]},
                "build_type": {'S': build_config["build_type"]},
                "joplin": {'S': build_config["joplin"]},
                "page_ids": {'L': [{'N': str(page_id)} for page_id in build_config["page_ids"]]},
                "env_vars": {'M': {'S': env_var for env_var in build_config["env_vars"]}},
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(deleted_build_item)
    write_item_batch.append(new_build_item)

    for req in assinged_reqs:
        # transact_write_items() allows a maximum of 25 TransactItems.
        # If there are more than 25 items, then start a new batch.
        if len(write_item_batch) >= 25:
            write_item_batches.append(write_item_batch)
            write_item_batch = []
        # reqs must be updated to remove build_id, and reset to status="waiting#{original timestamp}"
        updated_req_item = {
            "Update": {
                "TableName": table_name,
                "Key": {
                    "pk": {'S': req["pk"]},
                    "sk": {'S': req["sk"]},
                },
                "UpdateExpression": "REMOVE build_id SET failed_build_ids = list_append(if_not_exists(failed_build_ids, :empty_list), :failed_build_id), #s = :status",
                "ExpressionAttributeNames": { "#s": "status" },
                "ExpressionAttributeValues": {
                    # Reset status to original waiting status with original timestamp ("sk") to preserve request queuing order
                    ":status": {'S': f'waiting#{req["sk"]}'},
                    ":empty_list": {'L': []},
                    ":failed_build_id": {'L': [{'S': build_id}]},
                },
                "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
            }
        }
        write_item_batch.append(updated_req_item)
    write_item_batches.append(write_item_batch)

    for write_item_batch in write_item_batches:
        client.transact_write_items(TransactItems=write_item_batch)
