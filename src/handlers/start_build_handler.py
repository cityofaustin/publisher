import os, boto3, json
from boto3.dynamodb.conditions import Key, Attr
from copy import deepcopy

from .helpers.get_datetime import get_datetime


def start_build_handler(event, context):
    data = json.loads(event)["body"]
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    publisher_table = dynamodb.Table(f'coa_publisher_{os.getenv("DEPLOY_ENV")}')

    janis_branch = data["janis"]
    timestamp = get_datetime()

    building = publisher_table.get_item(
        Key={
            'pk': f'BLD#{janis_branch}',
            'sk': 'building',
        },
        ProjectionExpression='pk, sk, build_id',
    )
    if 'Item' in building:
        print("There is already a current build running")
    else:
        # Get all requests that have a "waiting" attribute.
        # Get them in reverse chronological order.
        # More recent requests take precedence over old requests
        # (in terms of values for "joplin" and "env_vars").
        # There would only be conflicts for "joplin" values on PR builds,
        # where multiple joplins could potentially update the same janis instance.
        reqs = publisher_table.query(
            IndexName="janis.waiting",
            Select='ALL_ATTRIBUTES',
            ConsistentRead=True,
            ScanIndexForward=False,
            KeyConditionExpression= Key('pk').eq(f'REQ#{janis_branch}') & Key('waiting').begins_with('waiting')
        )['Items']

        if len(reqs):
            build_id = f'BLD#{janis_branch}#{timestamp}'
            build_config = {
                "build_id": build_id,
                "build_type": "incremental",
                "page_ids": [],
            }

            for req in reqs:
                # unset "waiting" attribute on req
                req["waiting"] = None

                # Handle "joplin" attribute
                if not "joplin" in build_config:
                    # The most recent request will set the value of "joplin" for the build
                    build_config["joplin"] = req["joplin"]
                else:
                    # If req is for a different joplin, then cancel it.
                    if req["joplin"] != build_config["joplin"]:
                        req["canceled_by"] = build_id
                        continue

                # set "build_id" attribute on req
                req["build_id"] = build_id

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

                # Add "page_ids" and remove duplicates
                build_config["page_ids"] = list(set(
                    build_config["page_ids"] + req["page_ids"]
                ))

            print("hi")
            # Take all the requests and make a new build

            # res = client.transact_write_items(TransactItems=[
            #     {
            #         'ConditionCheck': {
            #             'Key':
            #         }
            #     }
            # ])



    print("hi")
    # Get all requests for a janis
    # Create a build

if __name__ == "__main__":
    start_build_handler('', '')
