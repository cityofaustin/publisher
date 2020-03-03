import os, boto3, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))  # Allows absolute import of "helpers" as a module

from helpers.utils import get_datetime


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
    dynamodb = boto3.resource('dynamodb')
    publisher_table = dynamodb.Table(f'coa_publisher_{os.getenv("DEPLOY_ENV")}')
    timestamp = get_datetime()

    # Validate body
    body = event.get("body")
    if not body:
        return failure_res("No 'body' passed with request.")
    data = json.loads(body)

    # Validate janis_branch
    janis_branch = data.get("janis_branch")
    if not janis_branch:
        return failure_res("janis_branch is required")
    pk = f'REQ#{janis_branch}'
    sk = timestamp
    status = f'waiting#{timestamp}'

    # Validate joplin_appname
    joplin = data.get("joplin_appname")
    if not joplin:
        return failure_res("joplin_appname is required")

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

    # Validate page_ids
    req_page_ids = data.get("page_ids")
    if not req_page_ids:
        page_ids = []
    else:
        if not isinstance(req_page_ids, list):
            return failure_res(f'page_ids must be a list.')
        for page_id in req_page_ids:
            if not isinstance(page_id, int):
                return failure_res(f'page_id [{page_id}] is not an integer.')
        page_ids = req_page_ids

    # Validate env_vars
    req_env_vars = data.get("env_vars")
    env_vars = {}
    if req_env_vars:
        if not isinstance(req_env_vars, dict):
            return failure_res(f'env_vars must be a dict.')
        for name, value in req_env_vars.items():
            if not isinstance(name, str):
                return failure_res(f'key {name} in env_vars must be a string.')
            if not isinstance(value, str):
                return failure_res(f'value {value} in env_vars must be a string.')
        env_vars = req_env_vars

    publisher_table.put_item(
        Item={
            'pk': pk,
            'sk': sk,
            'status': status,
            'page_ids': page_ids,
            'joplin': joplin,
            'env_vars': env_vars,
            'build_type': build_type,
        }
    )

    print(f"##### Submitted Publish Request pk={pk}, sk={sk}")

    return {
        "statusCode": 200,
        'headers': {'Content-Type': 'application/json'},
        "body": json.dumps({
            "request_id": f'{pk}#{sk}',
        })
    }
