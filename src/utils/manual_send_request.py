from os import path
import sys
sys.path.append(path.join(path.dirname(__file__), '../handlers'))

import os, json, requests
from publish_request_handler import handler

headers = {
    "x-api-key": os.getenv("COA_PUBLISHER_DEV_API_KEY"),
    "content-type": "application/json",
}
url = os.getenv("PUBLISH_REQUEST_URL")
data = {
    "janis_branch": os.getenv("JANIS_BRANCH"),
    "pages": [],
    "joplin_appname": os.getenv("JOPLIN"),
    "env_vars": {
        "REACT_STATIC_PREFETCH_RATE": "0",
    },
    "build_type": "rebuild",
}


res = requests.post(url, data=json.dumps(data), headers=headers)
print(res)
print(res.json())
