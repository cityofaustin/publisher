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

build_item = get_build_item("BLD#master#2020-07-12T15:28:04.697734-05:00")

pages = json.loads(json.dumps({
    "pages": build_item["pages"],
}, default=stringify_decimal))

print(pages)
