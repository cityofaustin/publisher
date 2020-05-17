import pytest
from botocore.exceptions import ParamValidationError

from tests.helpers.write_transaction import write_transaction
from helpers.utils import dynamoify, dynamoify_each, get_datetime


def test_write_pk_sk(dynamo_client):
    item = {
        "pk": {"S": "BLD#test"},
        "sk": {"S": get_datetime()},
    }
    write_transaction(dynamo_client, item)
    print("hi")


def test_put_dict_with_none(dynamo_client):
    bad_dynamoified_item = {
        "pk": dynamoify("BLD#test"),
        "sk": dynamoify(get_datetime()),
        "bad_dict": {
            'M': {
                "apple": None
            }
        }
    }
    pytest.raises(ParamValidationError, write_transaction, dynamo_client, bad_dynamoified_item)


def test_put_empty_string(dynamo_client):
    bad_dynamoified_item = {
        "pk": dynamoify("BLD#test"),
        "sk": dynamoify(get_datetime()),
        "empty": ""
    }
    pytest.raises(ParamValidationError, write_transaction, dynamo_client, bad_dynamoified_item)
