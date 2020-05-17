import os, boto3

def write_transaction(dynamo_client, item):
    new_build_item = {
        "Put": {
            "TableName": "coa_publisher_pytest",
            "Item": item,
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",
        }
    }
    write_item_batch = [
        new_build_item
    ]
    dynamo_client.transact_write_items(TransactItems=write_item_batch)
