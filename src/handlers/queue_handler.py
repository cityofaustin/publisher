import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from commands.start_new_build import start_new_build
from commands.process_new_build import process_new_build


def handler(event, context):
    for record in event['Records']:
        print(record)
        event_name = record['eventName']
        pk = record['dynamodb']['Keys']["pk"]["S"]

        # If we got a new request, see if we can start a build
        # pk = "REQ#[janis_branch]#[timestamp]"
        if (
            (event_name == "INSERT") and
            (pk.startswith("REQ"))
        ):
            janis_branch = pk.split("#")[1]
            print("##### New publish request submitted.")
            start_new_build(janis_branch, context)
        # If we get a new BLD, then start the build process
        # pk = "BLD#[janis_branch]#[timestamp]"
        elif (
            (event_name == "INSERT") and
            (pk.startswith("BLD"))
        ):
            build_id = record["dynamodb"]["NewImage"]["build_id"]["S"]
            process_new_build(build_id, context)
