import os, boto3, json
from boto3.dynamodb.conditions import Key, Attr


def send_request_handler(event, context):
    data = json.loads(event["body"])
    dynamo_client = boto3.client('dynamodb')
    # if janis.building
    # if janis.error
    # if janis.queued
    # else

    janis_branch = os.getenv("JANIS_BRANCH")
    build_table = f'coa_publisher_{os.getenv("DEPLOY_ENV")}_builds'
    requests_table = f'coa_publisher_{os.getenv("DEPLOY_ENV")}_requests'
    def update():
        item_building = dynamo_client.get_item(
            TableName=build_table,
            Key={
                "janis": {"S": janis_branch},
            }
        )

        print("congratulations")

    update()

if __name__ == "__main__":
    send_request_handler('', '')
