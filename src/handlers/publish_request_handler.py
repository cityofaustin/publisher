import os, boto3, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))  # Allows absolute import of "helpers" as a module

from helpers.utils import \
    get_datetime, DEPLOY_ENV, \
    is_staging, is_production, \
    get_dynamodb_table, \
    staging_janis_branch, staging_joplin_appname, \
    production_janis_branch, production_joplin_appname, \
    has_empty_strings, PublisherDynamoError
from helpers.valid_optional_env_vars import valid_optional_env_vars


def failure_res(message):
    print(f"##### Rejected Publish Request")
    print(f"##### {message}")
    return {
        "statusCode": 422,
        'headers': {'Content-Type': 'application/json'},
        "body": json.dumps({
            "message": message,
        })
    }


def handler(event, context):
    queue_table = get_dynamodb_table()
    timestamp = get_datetime()

    # Validate body
    body = event.get("body")
    if not body:
        return failure_res("No 'body' passed with request.")
    data = json.loads(body)

    # Validate joplin_appname
    joplin = data.get("joplin_appname")
    if not joplin:
        return failure_res("joplin_appname is required")

    # Validate janis_branch
    janis_branch = data.get("janis_branch")
    if not janis_branch:
        return failure_res("janis_branch is required")
    if janis_branch == staging_janis_branch:
        if not is_staging():
            return failure_res("Can only deploy to staging Janis from 'staging' Publisher.")
        if joplin != staging_joplin_appname:
            return failure_res(f"Can only deploy to staging Janis from {staging_joplin_appname}.")
    if janis_branch == production_janis_branch:
        if not is_production():
            return failure_res("Can only deploy to production Janis from 'production' Publisher.")
        if joplin != production_joplin_appname:
            return failure_res(f"Can only deploy to production Janis from {production_joplin_appname}.")
    # The DEPLOY_ENV determines custom deployment logic.
    # Make sure that the right Janis is being deployed to Production or Staging.
    if is_staging() and (janis_branch != staging_janis_branch):
            return failure_res("'staging' Publisher can only deploy to staging Janis.")
    if is_production() and (janis_branch != production_janis_branch):
            return failure_res("'production' Publisher can only deploy to production Janis.")

    pk = f'REQ#{janis_branch}'
    sk = timestamp
    status = f'waiting#{timestamp}'

    # Validate build_type
    build_type = data.get("build_type")
    valid_build_types = [
        "rebuild",
        "incremental",
        "all_pages",
    ]
    if (
        not build_type or
        build_type not in valid_build_types
    ):
        return failure_res(f'[{build_type}] is not a valid build_type.')

    # Validate pages
    api_key = data.get("api_key")
    req_pages = data.get("pages")
    if not req_pages:
        pages = []
    else:
        if not isinstance(req_pages, list):
            return failure_res(f'pages must be a list.')
        if has_empty_strings(req_pages):
            return failure_res(f'Empty strings are not allowed in pages.')
        for page in req_pages:
            page["timestamp"] = timestamp

        # The api_key is used to send a response back to Joplin on publish success.
        # Not required for all requests, only ones that have specific pages that must be updated.
        if not api_key:
            return failure_res("api_key is required when updating specific pages")

        pages = req_pages

    # Validate env_vars
    req_env_vars = data.get("env_vars")
    env_vars = {}
    if req_env_vars:
        if not isinstance(req_env_vars, dict):
            return failure_res(f'env_vars must be a dict.')
        if has_empty_strings(req_env_vars):
            return failure_res(f'Empty strings are not allowed in env_vars.')
        for name, value in req_env_vars.items():
            if name not in valid_optional_env_vars:
                return failure_res(f'env_var {name} is not a valid_optional_env_var.')
        env_vars = req_env_vars

    queue_table.put_item(
        Item={
            'pk': pk,
            'sk': sk,
            'status': status,
            'pages': pages,
            'joplin': joplin,
            'env_vars': env_vars,
            'build_type': build_type,
            'api_key': api_key,
        }
    )

    print(f"##### Submitted Publish Request pk={pk}, sk={sk}")

    return {
        "statusCode": 200,
        'headers': {'Content-Type': 'application/json'},
        "body": json.dumps({
            "pk": pk,
            "sk": sk
        })
    }
