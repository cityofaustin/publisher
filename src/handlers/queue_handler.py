from helpers.build_start import build_start


def handler(event, context):
    for record in event['Records']:
        event_name = record['eventName']
        new_item = record['dynamodb']['Keys']
        pk = new_item["pk"]["S"]
        janis_branch = pk.split("#")[1]

        # If we got a new request, see if we can start a build
        if (
            (event_name == "INSERT") and
            (pk.startswith("REQ"))
        ):
            print("##### New publish request submitted.")
            build_start(janis_branch)
