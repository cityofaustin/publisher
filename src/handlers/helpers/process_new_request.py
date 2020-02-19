import os, boto3, json
from boto3.dynamodb.conditions import Key

from helpers.utils import get_datetime, get_lambda_cloudwatch_url, get_current_build_item
import helpers.stages as stages


def process_new_request(janis_branch, context):
    print("##### New publish request submitted.")
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)
    timestamp = get_datetime()

    build_item = get_current_build_item(janis_branch)
    if build_item:
        print(f"##### No new build started. There is already a current build running for [{janis_branch}].")
        return None

    # Construct a build out of the waiting requests for a janis.
    # Get all requests that have a "waiting" attribute in reverse chronological order.
    # More recent request config values take precedence over old requests
    # (in terms of values for "joplin" and "env_vars").
    # There would only be conflicts for "joplin" values on PR builds,
    # where multiple joplins could potentially update the same janis instance.
    req_pk = f'REQ#{janis_branch}'
    waiting_reqs = publisher_table.query(
        IndexName="janis.status",
        Select='ALL_ATTRIBUTES',
        ScanIndexForward=False, # Return reqests in reverse chronological order (most recent first)
        KeyConditionExpression= Key('pk').eq(req_pk) & Key('status').begins_with('waiting')
    )['Items']

    if not len(waiting_reqs):
        print(f"##### No new build started. No requests to process for {janis_branch}.")
        return None

    build_id = f'BLD#{janis_branch}#{timestamp}'
    build_pk = f'BLD#{janis_branch}'
    build_config = {
        "build_id": build_id,
        "build_type": None,
        "joplin": None,
        "page_ids": [],
        "env_vars": {},
    }
    updated_req_configs = []

    # Construct build_config based on values from requests
    # Modify reqs with updated data
    for req in waiting_reqs:
        updated_req = {
            "pk": req["pk"],
            "sk": req["sk"],
        }
        updated_req_configs.append(updated_req)

        # Handle "joplin" attribute
        if not build_config["joplin"]:
            # The most recent request will set the value of "joplin" for the build
            build_config["joplin"] = req["joplin"]
        else:
            # If req is for a different joplin, then cancel it.
            if req["joplin"] != build_config["joplin"]:
                updated_req["canceled_by"] = build_id
                # A "cancelled" req will not have a "build_id" attribute assigned to it
                # And the data from a "cancelled" req should not be added to the build_config
                continue
        updated_req["build_id"] = build_id

        # Handle "env_vars" attribute
        for env_var in req["env_vars"]:
            # Only add env_var value if it hasn't already been added.
            # Otherwise more recent request env_vars would be overwritten by older requests.
            if env_var not in build_config["env_vars"]:
                build_config["env_vars"][env_var] = req["env_vars"][env_var]

        # Handle "build_type" attribute
        if req["build_type"] == "rebuild":
            build_config["build_type"] = "rebuild"
        elif (
            (req["build_type"] == "all_pages") and
            (build_config["build_type"] != "rebuild")
        ):
            build_config["build_type"] = "all_pages"
        elif (
            (req["build_type"] == "incremental") and
            (build_config["build_type"] != "rebuild") and
            (build_config["build_type"] != "all_pages")
        ):
            build_config["build_type"] = "incremental"

        # Add "page_ids", exclude duplicates
        build_config["page_ids"] = list(set(
            build_config["page_ids"] + req["page_ids"]
        ))

    write_item_batches = []
    write_item_batch = []
    new_current_build_item = {
        "Put": {
            "TableName": table_name,
            "Item": {
                "pk": {'S': "CURRENT_BLD"},
                "sk": {'S': janis_branch},
                "build_id": {'S': build_config["build_id"]},
            },
            # ConditionExpression makes sure that there isn't another build process already running for the same janis_branch
            "ConditionExpression": "attribute_not_exists(build_id)",
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    new_build_item = {
        "Put": {
            "TableName": table_name,
            "Item": {
                "pk": {'S': build_pk},
                "sk": {'S': timestamp},
                "build_id": {'S': build_config["build_id"]},
                "status": {'S': "building"},
                "stage": {'S': stages.preparing_to_build},
                "build_type": {'S': build_config["build_type"]},
                "joplin": {'S': build_config["joplin"]},
                "page_ids": {'L': [{'N': str(page_id)} for page_id in build_config["page_ids"]]},
                "env_vars": {'M': {key: {'S': value} for (key, value) in build_config["env_vars"]}},
                "logs": {'L': [
                    {
                        'M': {
                            'stage': {'S': stages.preparing_to_build},
                            'url': {'S': get_lambda_cloudwatch_url(context)},
                        }
                    }
                ]},
            },
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(new_current_build_item)
    write_item_batch.append(new_build_item)

    for updated_req in updated_req_configs:
        # transact_write_items() allows a maximum of 25 TransactItems.
        # If there are more than 25 items, then start a new batch.
        if len(write_item_batch) >= 25:
            write_item_batches.append(write_item_batch)
            write_item_batch = []

        UpdateExpression = "SET #s = :status"
        ExpressionAttributeNames = { "#s": "status" } # because "status" is a reserved word, you can't explicitly use it in an UpdateExpression
        ExpressionAttributeValues = {}
        if "canceled_by" in updated_req:
            UpdateExpression = UpdateExpression + ", canceled_by = :canceled_by"
            ExpressionAttributeValues[":status"] = {'S': f'cancelled#{timestamp}'}
            ExpressionAttributeValues[":canceled_by"] = {'S': updated_req["canceled_by"]}
        if "build_id" in updated_req:
            UpdateExpression = UpdateExpression + ", build_id = :build_id"
            ExpressionAttributeValues[":status"] = {'S': f'assigned#{timestamp}'}
            ExpressionAttributeValues[":build_id"] = {'S': updated_req["build_id"]}
        updated_req_item = {
            "Update": {
                "TableName": table_name,
                "Key": {
                    "pk": {'S': updated_req["pk"]},
                    "sk": {'S': updated_req["sk"]},
                },
                "UpdateExpression": UpdateExpression,
                "ExpressionAttributeNames": ExpressionAttributeNames,
                "ExpressionAttributeValues": ExpressionAttributeValues,
                "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
            }
        }
        write_item_batch.append(updated_req_item)
    write_item_batches.append(write_item_batch)

    for write_item_batch in write_item_batches:
        client.transact_write_items(TransactItems=write_item_batch)
    print(f"##### Started build for {janis_branch}: build_id={build_id}")
