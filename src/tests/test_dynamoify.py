import pytest
import boto3, os
from helpers.utils import dynamoify, get_datetime


# Can we dynamoify a string?
def test_dynamoify_string():
    data = "hello world"
    expected = {
        "S": "hello world"
    }
    assert dynamoify(data) == expected


# Can we dynamoify a number?
def test_dynamoify_number():
    data = 4
    expected = {
        "N": 4
    }
    assert dynamoify(data) == expected


# Can we dynamoify a list?
def test_dynamoify_list():
    data = ["hello world", "goodbye world", 3]
    expected = {"L": [
        {
            "S": "hello world"
        },
        {
            "S": "goodbye world"
        },
        {
            "N": 3
        },
    ]}
    assert dynamoify(data) == expected


# Can we dynamoify a nested list?
def test_dynamoify_nested_list():
    data = ["a", "b", ["c", "d", ["e", "f"]]]
    expected = {
        "L": [
            {
                "S": "a"
            },
            {
                "S": "b"
            },
            {
                "L": [
                    {"S": "c"},
                    {"S": "d"},
                    {"L": [
                        {"S": "e"},
                        {"S": "f"},
                    ]}
                ]
            },
        ]
    }
    assert dynamoify(data) == expected


# Can we dynamoify a dictionary?
def test_dynamoify_dict():
    data = {
        "a": "first",
        "b": "second",
        "c": "third",
    }
    expected = {
        'M': {
            "a": {"S": "first"},
            "b": {"S": "second"},
            "c": {"S": "third"},
        }
    }
    assert dynamoify(data) == expected


# Can we dynamoify a nested dict?
def test_dynamoify_nested_dict():
    data = {
        "a": {
            "aa": "apple",
            "ab": "pie"
        },
        "b": {
            "bb": {
                "bbb": "banana"
            }
        },
        "c": "third",
    }
    expected = {
        'M': {
            "a": {
                "M": {
                    "aa": {"S": "apple"},
                    "ab": {"S": "pie"},
                }
            },
            "b": {
                "M": {
                    "bb": {
                        "M": {
                            "bbb": {
                                "S": "banana"
                            }
                        }
                    }
                }
            },
            "c": {"S": "third"},
        }
    }
    assert dynamoify(data) == expected


# Can we dynamoify a list in a dict?
def test_dynamoify_list_in_dict():
    data = {
        "a": {
            "aa": "apple",
            "ab": "pie"
        },
        "b": [
            "bb",
            "bbc"
        ],
        "c": "third",
    }
    expected = {
        'M': {
            "a": {
                "M": {
                    "aa": {"S": "apple"},
                    "ab": {"S": "pie"},
                }
            },
            "b": {
                "L": [
                    {"S": "bb"},
                    {"S": "bbc"},
                ]
            },
            "c": {"S": "third"},
        }
    }


# Can we dynamoify a list in a dict?
def test_dynamoify_list_in_dict():
    data = {
        "a": {
            "aa": "apple",
            "ab": "pie"
        },
        "b": [
            "bb",
            "bbc"
        ],
        "c": "third",
    }
    expected = {
        'M': {
            "a": {
                "M": {
                    "aa": {"S": "apple"},
                    "ab": {"S": "pie"},
                }
            },
            "b": {
                "L": [
                    {"S": "bb"},
                    {"S": "bbc"},
                ]
            },
            "c": {"S": "third"},
        }
    }
    assert dynamoify(data) == expected


# Can we dynamoify a dict in a list?
def test_dynamoify_dict_in_list():
    data = ["a", "b", {"c": "d", "e": {"f": "g"}}]
    expected = {
        "L": [
            {
                "S": "a"
            },
            {
                "S": "b"
            },
            {
                "M": {
                    "c": {"S": "d"},
                    "e": {
                        "M": {
                            "f": {"S": "g"}
                        }
                    }
                }
            },
        ]
    }
    assert dynamoify(data) == expected


# def test_insert_map():
#     boto3.client('dynamodb', endpoint_url=f'http://localhost:{os.getenv("PUBLISHER_DYNAMODB_PORT")}')
#     data = {
#         "pk": "REQ#test",
#         "sk": get_datetime(),
#     }
#     expected = {
#         "S": "hello world"
#     }
#     assert dynamoify(data) == expected
