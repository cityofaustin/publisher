import requests, json

from helpers.utils import get_joplin_url, stringify_decimal


def send_publish_succeeded_message(build_item):
    # Only send a message back to Joplin if our BLD contains requests that were publish_requests from Joplin
    if (build_item.get("api_keys") and len(build_item["api_keys"]) > 0):
        joplin_url = get_joplin_url(build_item["joplin"])
        res = requests.post(
            url=f"{joplin_url}/publish_succeeded",
            data=json.dumps({
                "pages": build_item["pages"],
                "api_keys": build_item["api_keys"]
            }, default=stringify_decimal),
            headers={
                "Content-Type": "application/json",
                # Joplin-Api-Key Header name set by API_KEY_CUSTOM_HEADER setting in Joplin
                "Joplin-Api-Key": build_item["api_keys"][0]
            },
        )
        if res.status_code != 200:
            print(f"publish_succeeded_message failed with status {res.status_code}")
            print(f"message: {res.json()['message']}")
            raise Exception(f"publish_succeeded_message failed: {res.json()['message']}")
