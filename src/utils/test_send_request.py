from os import path
import sys
sys.path.append(path.join(path.dirname(__file__), '../handlers'))

import os, json, requests
from publish_request_handler import handler

headers = {
    "x-api-key": os.getenv("COA_PUBLISHER_TEST_DEV_API_KEY"),
    "content-type": "application/json",
}
url = os.getenv("PUBLISH_REQUEST_URL")
data = {
    "janis_branch": os.getenv("JANIS_BRANCH"),
    "page_ids": [],
    "joplin_appname": f'joplin-staging',
    "env_vars": {
        "REACT_STATIC_PREFETCH_RATE": "5",
    },
    "build_type": "rebuild",
}


res = requests.post(url, data=json.dumps(data), headers=headers)
print(res.json())
