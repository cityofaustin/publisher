from helpers.process_new_build import process_new_build
from helpers.process_new_request import process_new_request


def handler(event, context):
    for record in event['Records']:
        event_name = record['eventName']
        new_item = record['dynamodb']['Keys']
        pk = new_item["pk"]["S"]
        sk = new_item["sk"]["S"]
        janis_branch = pk.split("#")[1]

        # print("#### event:")
        # print(event)
        # print("#### context:")
        # print(context)

        # If we got a new request, see if we can start a build
        if (
            (event_name == "INSERT") and
            (pk.startswith("REQ"))
        ):
            print("##### New publish request submitted.")
            process_new_request(janis_branch)
        # If we get a new build submission, start the build
        elif (
            (event_name == "INSERT") and
            (pk.startswith("BLD")) and
            (sk == "building")
        ):
            print("##### New build request submitted.")
            process_new_build(janis_branch)
