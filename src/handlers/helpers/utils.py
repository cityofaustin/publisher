import os, boto3, re
from datetime import datetime
from pytz import timezone


class PublisherDynamoError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return 'Error with dynamodb data.'


# Returns the current datetime in central time
def get_datetime():
    return datetime.now(timezone('US/Central')).isoformat()


# Get the URL for the logs of the current lambda function invocation
def get_lambda_cloudwatch_url(context):
    return f'https://console.aws.amazon.com/cloudwatch/home?region={os.getenv("AWS_REGION")}#logEventViewer:group={context.log_group_name};stream={context.log_stream_name}'


# Extract pk and sk from a build_id
# build_pk, build_sk = parse_build_id(build_id)
def parse_build_id(build_id):
    build_meta_data = build_id.split('#')
    build_pk = '#'.join(build_meta_data[0:2])
    build_sk = build_meta_data[2]
    return (build_pk, build_sk)


# Get data for the BLD that's currently runnning for a janis_branch
# Returns None if there isn't a CURRENT_BLD build_id set
def get_current_build_item(janis_branch):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'coa_publisher_{os.getenv("DEPLOY_ENV")}'
    publisher_table = dynamodb.Table(table_name)

    # Get the CURRENT_BLD for your janis_branch
    current_build_item = publisher_table.get_item(
        Key={
            'pk': "CURRENT_BLD",
            'sk': janis_branch,
        },
        ProjectionExpression='build_id',
    )
    # Check if there isn't a CURRENT_BLD for your janis_branch
    # or if the CURRENT_BLD item doesn't have an assigned build_id (which means there is no build currently running)
    if (
        (not 'Item' in current_build_item) or
        (not current_build_item['Item'].get('build_id'))
    ):
        print(f'##### No CURRENT_BLD found for [{janis_branch}].')
        return None

    # Get the BLD item for your CURRENT_BLD
    build_id = current_build_item['Item']['build_id']
    build_pk, build_sk = parse_build_id(build_id)
    build = publisher_table.get_item(
        Key={
            'pk': build_pk,
            'sk': build_sk,
        },
    )
    if (not 'Item' in build):
        raise PublisherDynamoError(f'CURRENT_BLD for [{build_id}] does not have a corresponding BLD item.')

    return build['Item']


# Convert github branch_name to a legal name for an aws container
# Replaces any non letter, number or "-" characters with "-"
# 255 character limit
def github_to_aws(branch_name):
    return re.sub('[^\w\d-]','-',branch_name)[:255]
