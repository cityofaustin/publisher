import os

# Get the URL for the logs of the current lambda function invocation
def get_lambda_cloudwatch_url(context):
    return f'https://console.aws.amazon.com/cloudwatch/home?region={os.getenv("AWS_REGION")}#logEventViewer:group={context.log_group_name};stream={context.log_stream_name}'
