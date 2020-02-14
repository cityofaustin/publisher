import os, boto3, json
from boto3.dynamodb.conditions import Key, Attr
from copy import deepcopy

from .helpers.get_datetime import get_datetime

def create_req_transact_item(updated_waiting_req):
    UpdateExpression = "REMOVE waiting" # remove the "waiting" attribute so we don't reprocess this request
    ExpressionAttributeValues = {}
    if "canceled_by" in updated_waiting_req:
        UpdateExpression = UpdateExpression + " SET canceled_by = :canceled_by"
        ExpressionAttributeValues[":canceled_by"] = {'S': updated_waiting_req["canceled_by"]}
    if "build_id" in updated_waiting_req:
        UpdateExpression = UpdateExpression + " SET build_id = :build_id"
        ExpressionAttributeValues[":build_id"] = {'S': updated_waiting_req["build_id"]}

    return {
        "Update": {
            "TableName": f'coa_publisher_{os.getenv("DEPLOY_ENV")}',
            "Key": {
                "pk": {'S': updated_waiting_req["pk"]},
                "sk": {'S': updated_waiting_req["sk"]},
            },
            "UpdateExpression": UpdateExpression,
            "ExpressionAttributeValues": ExpressionAttributeValues,
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }


def build_start_handler(event, context):
    data = json.loads(event)["body"]
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    publisher_table = dynamodb.Table(f'coa_publisher_{os.getenv("DEPLOY_ENV")}')

    janis_branch = data["janis"]
    build_pk = f'BLD#{janis_branch}'
    timestamp = get_datetime()

    building = publisher_table.get_item(
        Key={
            'pk': build_pk,
            'sk': 'building',
        },
        ProjectionExpression='pk, sk, build_id',
    )
    # if 'Item' in building:
    #     print("There is already a current build running")
    #     return None

    # Construct a build out of the waiting requests for a janis.
    # Get all requests that have a "waiting" attribute in reverse chronological order.
    # More recent request config values take precedence over old requests
    # (in terms of values for "joplin" and "env_vars").
    # There would only be conflicts for "joplin" values on PR builds,
    # where multiple joplins could potentially update the same janis instance.
    waiting_reqs = publisher_table.query(
        IndexName="janis.waiting",
        Select='ALL_ATTRIBUTES',
        ConsistentRead=True,
        ScanIndexForward=False, # Return reqests in reverse chronological order (most recent first)
        KeyConditionExpression= Key('pk').eq(f'REQ#{janis_branch}') & Key('waiting').begins_with('waiting')
    )['Items']

    if not len(waiting_reqs):
        print("No requests to process")
        return None

    build_config = {
        "build_id": f'BLD#{janis_branch}#{timestamp}',
        "build_type": None,
        "joplin": None,
        "page_ids": [],
        "env_vars": {},
    }
    updated_waiting_reqs = []

    # Construct build_config based on values from requests
    # Modify reqs with updated data
    for req in waiting_reqs:
        updated_waiting_req = {
            "pk": req["pk"],
            "sk": req["sk"],
        }
        updated_waiting_reqs.append(updated_waiting_req)

        # Handle "joplin" attribute
        if not build_config["joplin"]:
            # The most recent request will set the value of "joplin" for the build
            build_config["joplin"] = req["joplin"]
        else:
            # If req is for a different joplin, then cancel it.
            if req["joplin"] != build_config["joplin"]:
                updated_waiting_req["canceled_by"] = build_config["build_id"]
                # A "cancelled" req will not have a build_id assigned to it
                # And the data from a "cancelled" req should not be added to the build_config
                continue
        updated_waiting_req["build_id"] = build_config["build_id"]

        # Handle "env_vars" attribute
        for env_var in req["env_vars"]:
            # Only add env_var value if it hasn't already been added.
            # Otherwise more recent request env_vars would be overwritten by older requests.
            if env_var not in build_config:
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
    new_build_item = {
        "Put": {
            "TableName": f'coa_publisher_{os.getenv("DEPLOY_ENV")}',
            "Item": {
                "pk": {'S': build_pk},
                "sk": {'S': "building"},
                "build_id": {'S': build_config["build_id"]},
                "build_type": {'S': build_config["build_type"]},
                "joplin": {'S': build_config["joplin"]},
                "page_ids": {'L': [{'N': str(page_id)} for page_id in build_config["page_ids"]]},
                "env_vars": {'M': {'S': env_var for env_var in build_config["env_vars"]}},
            },
            "ConditionExpression": "attribute_not_exists(sk)", # make sure that another process with sk="building" hasn't started already
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch.append(new_build_item)
    for updated_waiting_req in updated_waiting_reqs:
        # transact_write_items() allows a maximum of 25 TransactItems.
        # If there are more than 25 items, then start a new batch.
        if len(write_item_batch) >= 25:
            write_item_batches.append(write_item_batch)
            write_item_batch = []
        write_item_batch.append(create_req_transact_item(updated_waiting_req))
    write_item_batches.append(write_item_batch)

    for batch in write_item_batches:
        client.transact_write_items(TransactItems=batch)

    print("hi")

if __name__ == "__main__":
    build_start_handler('', '')
