import os, boto3, re, io
from datetime import datetime
from pytz import timezone

from helpers.valid_optional_env_vars import valid_optional_env_vars

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


DEPLOY_ENV = os.getenv("DEPLOY_ENV")
def is_staging():
    return DEPLOY_ENV == "staging"
def is_production():
    return DEPLOY_ENV == "production"
table_name = f'coa_publisher_{DEPLOY_ENV}'


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


def get_janis_branch(build_id):
    return build_id.split("#")[1]


# Returns build_item for a build_id
def get_build_item(build_id):
    dynamodb = boto3.resource('dynamodb')
    queue_table = dynamodb.Table(table_name)

    build_pk, build_sk = parse_build_id(build_id)
    build = queue_table.get_item(
        Key={
            'pk': build_pk,
            'sk': build_sk,
        },
    )
    if (not 'Item' in build):
        raise PublisherDynamoError(f'#### BLD [{build_id}] does not exist.')

    return build['Item']


# Get data for the BLD that's currently runnning for a janis_branch
# Returns None if there isn't a CURRENT_BLD build_id set
def get_current_build_item(janis_branch):
    dynamodb = boto3.resource('dynamodb')
    queue_table = dynamodb.Table(table_name)

    # Get the CURRENT_BLD for your janis_branch
    current_build_item = queue_table.get_item(
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
    return get_build_item(build_id)


# Convert github branch_name to a legal name for an aws container
# Replaces any non letter, number or "-" characters with "-"
# 255 character limit
def github_to_aws(branch_name):
    return re.sub('[^\w\d-]','-',branch_name)[:255]


# Retrieve latest task definition ARN (with revision number)
# Returns "None" if one doesn't exist
def get_latest_task_definition(janis_branch):
    ecs_client = boto3.client('ecs')

    task_definitions = ecs_client.list_task_definitions(
        # family is set in register_janis_builder_task()
        familyPrefix=f'janis-builder-{janis_branch}',
        sort="DESC",
        maxResults=1,
    )['taskDefinitionArns']

    if len(task_definitions):
        return task_definitions[0]
    else:
        return None


def get_cms_api_url(joplin):
    return f'https://{joplin}.herokuapp.com/api/graphql'


def get_cms_media_url(janis_branch):
    if is_production():
        return 'https://joplin-austin-gov-static.s3.amazonaws.com/production/media'
    else:
        return 'https://joplin-austin-gov-static.s3.amazonaws.com/staging/media'


# DEPLOYMENT_MODE is a setting used within Janis to set environment-specific configs.
def get_deployment_mode():
    if is_production():
        return 'PRODUCTION'
    elif is_staging():
        return "STAGING"
    else:
        return "REVIEW"


def get_cms_docs(janis_branch):
    if is_production():
        return 'https://joplin-austin-gov-static.s3.amazonaws.com/production/media/documents'
    else:
        return 'multiple'


def get_google_analytics():
    if is_production():
        return 'UA-110716917-2'
    else:
        return 'UA-000000000-0'


def get_cloudfront_distribution_id():
    if is_production() or is_staging():
        return os.getenv("CLOUDFRONT_DISTRIBUTION_ID")
    else:
        return None


# Netlify site names are limited to 63 characters
def get_netlify_site_name(janis_branch):
    if is_production() or is_staging():
        return None
    else:
        return (f'janis-v3-{janis_branch.lower()}')[:63]


'''
    These are the environment variables that get passed into janis_builder container.
    They are all accessible by janis_builder_base/scripts/build_site.sh
'''
def get_janis_builder_factory_env_vars(build_item):
    janis_branch = get_janis_branch(build_item["build_id"])
    required_env_vars = {
        "JANIS_BRANCH": janis_branch,
        "BUILD_ID": build_item["build_id"],
        "DEPLOYMENT_MODE": get_deployment_mode(),
        "NETLIFY_SITE_NAME": get_netlify_site_name(janis_branch),
        "CMS_API": get_cms_api_url(build_item["joplin"]),
        "CMS_MEDIA": get_cms_media_url(janis_branch),
        "CMS_DOCS": get_cms_docs(janis_branch),
        "GOOGLE_ANALYTICS": get_google_analytics(),
        "CLOUDFRONT_DISTRIBUTION_ID": get_cloudfront_distribution_id(),
    }

    optional_env_vars = {}
    for key, value in build_item["env_vars"].items():
        if key in valid_optional_env_vars:
            optional_env_vars[key] = value

    environmentVariablesOverride=[]
    for key, value in {**required_env_vars, **optional_env_vars}.items():
        # Skip empty values
        if value:
            environmentVariablesOverride.append({
                "name": key,
                "value": value,
                "type": "PLAINTEXT",
            })
    return environmentVariablesOverride


def get_zipped_janis_build(janis_branch):
    s3 = boto3.client('s3')
    bytes_buffer = io.BytesIO()
    s3.download_fileobj(
        Bucket='coa-publisher',
        Key=f'builds/{os.getenv("DEPLOY_ENV")}/janis#{janis_branch}.zip',
        Fileobj=bytes_buffer
    )
    data_binary = bytes_buffer.getvalue()
    return data_binary


def get_janis_branch(build_id):
    build_pk, build_sk = parse_build_id(build_id)
    janis_branch = build_pk.split('#')[1]
    return janis_branch
