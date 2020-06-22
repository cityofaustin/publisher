from os import path
import sys
import json
from decimal import Decimal
sys.path.append(path.join(path.dirname(__file__), '../handlers'))

from helpers.utils import get_dynamodb_table, get_build_item

queue_table = get_dynamodb_table()


def stringify_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    else:
        return obj

build_item = get_build_item("BLD#4356-queue#2020-06-12T16:08:55.091604-05:00")
print("hi")
