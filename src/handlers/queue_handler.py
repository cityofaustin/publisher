import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) # Allows absolute import of "helpers" as a module

from helpers.process_new_build import process_new_build
from helpers.process_new_request import process_new_request


def handler(event, context):
    for record in event['Records']:
        event_name = record['eventName']
        new_item = record['dynamodb']['Keys']
        pk = new_item["pk"]["S"]

        # If we got a new request, see if we can start a build
        # pk = "REQ#[janis_branch]#[timestamp]"
        if (
            (event_name == "INSERT") and
            (pk.startswith("REQ"))
        ):
            janis_branch = new_item["pk"]["S"].split("#")[1]
            process_new_request(janis_branch, context)
        # If we get a new BLD, then start the build process
        # pk = "BLD#[janis_branch]#[timestamp]"
        elif (
            (event_name == "INSERT") and
            (pk.startswith("BLD"))
        ):
            janis_branch = new_item["pk"]['S'].split("#")[1]
            process_new_build(janis_branch, context)
