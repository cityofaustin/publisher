import dateutil.parser
from boto3.dynamodb.conditions import Key
import json
import boto3
from slack_webhook import Slack

from helpers.utils import get_datetime, get_build_item, get_janis_branch, \
    table_name, get_dynamodb_table, get_dynamodb_client, is_production, \
    stringify_decimal


def process_build_failure(build_id, context):
    queue_table = get_dynamodb_table()
    client = get_dynamodb_client()
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
        KeyConditionExpression=Key('build_id').eq(build_id) & Key('pk').eq(req_pk)
    )['Items']

    write_item_batches = []
    write_item_batch = []
    updated_current_build_item = {
        "Update": {
            "TableName": table_name,
            "Key": {
                "pk": "CURRENT_BLD",
                "sk": janis_branch,
            },
            "UpdateExpression": "REMOVE build_id",
            "ConditionExpression": "build_id = :build_id",
            "ExpressionAttributeValues": {
                ":build_id": build_id,
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    updated_build_item = {
        "Update": {
            "TableName": table_name,
            "Key": {
                "pk": build_pk,
                "sk": build_sk,
            },
            "UpdateExpression": "SET #s = :status, total_build_time = :total_build_time",
            "ExpressionAttributeValues": {
                ":status": f'failed#{timestamp}',
                ":total_build_time": total_build_time,
            },
            "ExpressionAttributeNames": {
                "#s": "status"
            },
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
                    "pk": req["pk"],
                    "sk": req["sk"],
                },
                "UpdateExpression": "REMOVE build_id SET failed_build_ids = list_append(if_not_exists(failed_build_ids, :empty_list), :failed_build_id), #s = :status",
                "ExpressionAttributeNames": {
                    "#s": "status"
                },
                "ExpressionAttributeValues": {
                    # Reset status to original waiting status with original timestamp ("sk") to preserve request queuing order
                    ":status": f'waiting#{req["sk"]}',
                    ":empty_list": [],
                    ":failed_build_id": [build_id],
                },
            }
        }
        write_item_batch.append(updated_req_item)
    write_item_batches.append(write_item_batch)

    for write_item_batch in write_item_batches:
        client.transact_write_items(TransactItems=write_item_batch)
    print(f"##### Build failure processing for [{build_id}] is complete.")

    # Notify slack channel if there are errors in Production
    if is_production():
        ssm_client = boto3.client('ssm')
        webhook_url = ssm_client.get_parameter(Name="/coa-publisher/production/slack_webhook_publisher_errors", WithDecryption=True)['Parameter']['Value']
        # refreshed_build_item will have most up to date "logs" urls and "status"
        refreshed_build_item = get_build_item(build_id)
        slack_message = "Janis build failed\n"
        slack_message += f"```{json.dumps(refreshed_build_item, default=stringify_decimal, indent=4)}```"
        slack = Slack(url=webhook_url)
        slack.post(text=slack_message)
