import os, boto3, json


def handler(event, context):
    print("##### CodeBuild Finished")
    print(event["Records"][0]["Sns"])

    # If it failed, execute failure handler
    # Else, start the new task handler
