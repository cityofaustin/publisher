import requests, json

from helpers.utils import get_joplin_url


def send_publish_succeeded_message(build_item):
    joplin_url = get_joplin_url(build_item["joplin"])
    return requests.post(
        url=joplin_url,
        data=json.dumps({
            "pages": build_item["pages"],
            "api_keys": build_item["api_keys"]
        }),
        headers={
            "Content-Type": "application/json",
            # Joplin-Api-Key Header name set by API_KEY_CUSTOM_HEADER setting in Joplin
            "Joplin-Api-Key": build_item["api_keys"][0]
        },
    )
