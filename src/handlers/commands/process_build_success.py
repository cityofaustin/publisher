import os, boto3, json
import dateutil.parser

from helpers.utils import get_datetime, get_current_build_item


def process_build_success(janis_branch, context):
    client = boto3.client('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    timestamp = get_datetime()

    build_item = get_current_build_item(janis_branch)
    if not build_item:
        print(f'##### Successful build for [{janis_branch}] has already been handled')
        return None

    build_id = build_item["build_id"]
    build_pk = build_item["pk"]
    build_sk = build_item["sk"]
    start_build_time = dateutil.parser.parse(build_item["sk"])
    end_build_time = dateutil.parser.parse(timestamp)
    total_build_time = str(end_build_time - start_build_time)

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
                ":status": {'S': f'succeeded#{timestamp}'},
                ":total_build_time": {'S': total_build_time},
            },
            "ExpressionAttributeNames": { "#s": "status" },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(updated_current_build_item)
    write_item_batch.append(updated_build_item)
    client.transact_write_items(TransactItems=write_item_batch)
    print(f'##### Successful build for [{build_id}] complete.')
