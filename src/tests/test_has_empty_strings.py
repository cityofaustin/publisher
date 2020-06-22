import pytest

from helpers.utils import PublisherDynamoError, has_empty_strings


@pytest.mark.parametrize("data", [
    "a",
    ["a","b","c"],
    {
        "a": "apple",
        "b": "banana",
        "c": "cat"
    },
    {
        "a": "apple",
        "b": "banana",
        "c": [
            "hi",
            "there",
            {
                "d": "eggs",
                "e": "dog"
            }
        ],
        "d": "hi"
    }
])
def test_normal_strings(data):
    assert has_empty_strings(data) is False


@pytest.mark.parametrize("data", [
    "",
    ["","",""],
    ["x","s",""],
    ["x","s",{
        "a": {
            "b": ""
        }
    }],
    {
        "a": "apple",
        "b": "",
        "c": "cat"
    },
    {
        "a": "apple",
        "b": "banana",
        "c": [
            "hi",
            "there",
            {
                "d": "eggs",
                "e": ""
            }
        ],
        "d": "hi"
    }
])
def test_empty_strings(data):
    assert has_empty_strings(data) is True
