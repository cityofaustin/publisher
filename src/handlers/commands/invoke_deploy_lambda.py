import json, os, boto3


def invoke_deploy_lambda(janis_branch):
    lambda_client = boto3.client("lambda")
    payload_bytes = json.dumps({
        "janis_branch": janis_branch,
    }).encode('utf-8')
    lambda_client.invoke(
        FunctionName=os.getenv("DEPLOY_LAMBDA_ARN"),
        InvocationType='Event',
        Payload=payload_bytes
    )
