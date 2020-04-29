import os, boto3, json
import dateutil.parser
from boto3.dynamodb.conditions import Key

from helpers.utils import get_datetime, get_build_item, get_janis_branch, table_name


def process_build_failure(build_id, context):
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    queue_table = dynamodb.Table(table_name)
    timestamp = get_datetime()

    build_item = get_build_item(build_id)
    if build_item["status"] != "building":
        print(f"##### Failed build for [{build_id}] has already been handled")
        return None

    janis_branch = get_janis_branch(build_id)
    build_pk = build_item["pk"]
    build_sk = build_item["sk"]
    start_build_time = dateutil.parser.parse(build_item["sk"])
    end_build_time = dateutil.parser.parse(timestamp)
    total_build_time = str(end_build_time - start_build_time)

    req_pk = f'REQ#{janis_branch}'
    print(f"##### Build for [{build_id}] failed.")
    assinged_reqs = queue_table.query(
        IndexName="build_id.janis",
        Select='ALL_ATTRIBUTES',
        ScanIndexForward=True,
        KeyConditionExpression= Key('build_id').eq(build_id) & Key('pk').eq(req_pk)
    )['Items']

    write_item_batches = []
    write_item_batch = []
    updated_current_build_item = {
        "Update": {
            "TableName": table_name,
            "Key": {
                "pk": {'S': "CURRENT_BLD"},
                "sk": {'S': janis_branch},
            },
            "UpdateExpression": "REMOVE build_id",
            "ConditionExpression": "build_id = :build_id",
            "ExpressionAttributeValues": {
                ":build_id": {'S': build_id},
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    updated_build_item = {
        "Update": {
            "TableName": table_name,
            "Key": {
                "pk": {'S': build_pk},
                "sk": {'S': build_sk},
            },
            "UpdateExpression": "SET #s = :status, total_build_time = :total_build_time",
            "ExpressionAttributeValues": {
                ":status": {'S': f'failed#{timestamp}'},
                ":total_build_time": {'S': total_build_time},
            },
            "ExpressionAttributeNames": { "#s": "status" },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(updated_current_build_item)
    write_item_batch.append(updated_build_item)

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
            }
        }
        write_item_batch.append(updated_req_item)
    write_item_batches.append(write_item_batch)

    for write_item_batch in write_item_batches:
        client.transact_write_items(TransactItems=write_item_batch)
    print(f"##### Build failure processing for [{build_id}] is complete.")
