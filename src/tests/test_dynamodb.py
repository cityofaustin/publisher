import pytest
from botocore.exceptions import ClientError

from tests.helpers.write_transaction import write_transaction
from helpers.utils import get_datetime


# Test that a basic item can be inserted
def test_write_pk_sk(dynamodb_client):
    item = {
        "pk": "BLD#test",
        "sk": get_datetime(),
    }
    write_transaction(dynamodb_client, item)


# Test that an empty string fails as expected.
# Known limitation of dynamodb - you can't insert empty strings
def test_put_empty_string(dynamodb_client):
    bad_dynamoified_item = {
        "pk": "BLD#test",
        "sk": get_datetime(),
        "empty": ""
    }
    pytest.raises(ClientError, write_transaction, dynamodb_client, bad_dynamoified_item)


def test_put_empty_string_from_list(dynamodb_client):
    bad_dynamoified_item = {
        "pk": "BLD#test",
        "sk": get_datetime(),
        "empty": ["","hi"]
    }
    pytest.raises(ClientError, write_transaction, dynamodb_client, bad_dynamoified_item)
