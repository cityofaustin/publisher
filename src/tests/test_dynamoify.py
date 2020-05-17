import pytest
import boto3, os
from helpers.utils import dynamoify, dynamoify_each, get_datetime


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
    dynamoify_expected = {
        'M': {
            "a": {"S": "first"},
            "b": {"S": "second"},
            "c": {"S": "third"},
        }
    }
    dynamoify_each_expected = {
        "a": {"S": "first"},
        "b": {"S": "second"},
        "c": {"S": "third"},
    }
    assert dynamoify(data) == dynamoify_expected
    assert dynamoify_each(data) == dynamoify_each_expected


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
    dynamoify_expected = {
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
    dynamoify_each_expected = {
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
    assert dynamoify(data) == dynamoify_expected
    assert dynamoify_each(data) == dynamoify_each_expected


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
    dynamoify_expected = {
        'M': {
            "a":  {
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
    dynamoify_each_expected = {
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
    assert dynamoify(data) == dynamoify_expected
    assert dynamoify_each(data) == dynamoify_each_expected


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


def test_dynamoify_logs():
    data = [
        {
            "stage": "stage_one",
            "url": "www.demo.x",
        }
    ]
    expected = {'L': [
        {
            'M': {
                'stage': {'S': "stage_one"},
                'url': {'S': "www.demo.x"},
            }
        }
    ]}
    assert dynamoify(data) == expected


def test_dynamoify_empty_set():
    data = {}
    expected = None
    assert dynamoify(data) == expected


def test_dynamoify_empty_string():
    data = ""
    expected = None
    assert dynamoify(data) == expected


def test_dynamoify_list_with_empty_values():
    data = [None, ""]
    expected = {"L": []}
    assert dynamoify(data) == expected


def test_dynamoify_empty_values_in_dict():
    data = {
        "a": "apple",
        "b": None,
        "c": "",
        "d": {
            "a": "",
            "c": {
                "d": None
            }
        },
        "e": {
            "a": "",
            "c": {
                "d": "hi"
            }
        }
    }
    dynamoify_expected = {
        "M": {
            "a": {"S": "apple"},
            "e": {"M": {
                "c": {
                    "M": {
                        "d": {"S": "hi"}
                    }
                }
            }}
        }
    }
    dynamoify_each_expected = {
        "a": {"S": "apple"},
        "e": {"M": {
            "c": {
                "M": {
                    "d": {"S": "hi"}
                }
            }
        }}
    }
    assert dynamoify(data) == dynamoify_expected
    assert dynamoify_each(data) == dynamoify_each_expected


def test_dynamoify_empty_values_in_list():
    data = [
        None,
        "",
        [None, None, "c"],
        "d"
    ]
    expected = {
        "L": [
            {"L": [{"S": "c"}]},
            {"S": "d"}
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
