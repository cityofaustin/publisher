import pytest, json

from handlers.publish_request_handler import handler as publish_request_handler
from handlers.helpers.valid_optional_env_vars import valid_optional_env_vars
from handlers.helpers.utils import \
    staging_janis_branch, staging_joplin_appname, \
    production_janis_branch, production_joplin_appname


def make_event(data):
    return {
        "body": json.dumps(data)
    }


def test_no_body(patch_demo_table):
    context = {}
    event = {}
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "No 'body' passed with request."


def test_no_joplin_appname(patch_demo_table):
    context = {}
    event = make_event({"a": "apple"})
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "joplin_appname is required"


def test_no_janis_branch(patch_demo_table):
    context = {}
    event = make_event({
        "joplin_appname": "master"
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "janis_branch is required"


def test_deploy_to_staging_from_nonstaging_env(patch_demo_table):
    context = {}
    event = make_event({
        "joplin_appname": staging_joplin_appname,
        "janis_branch": staging_janis_branch
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "Can only deploy to staging Janis from 'staging' Publisher."


def test_deploy_to_staging_from_nonstaging_joplin(patch_demo_table, mocker):
    # Sets is_staging() validator to True
    # Allows us to pretend that this function is running on the staging Publisher
    mocker.patch('handlers.publish_request_handler.is_staging', return_value=True)
    context = {}
    event = make_event({
        "joplin_appname": "pr-not-staging",
        "janis_branch": staging_janis_branch
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f"Can only deploy to staging Janis from {staging_joplin_appname}."


def test_deploy_to_prod_from_nonprod_env(patch_demo_table):
    context = {}
    event = make_event({
        "joplin_appname": production_joplin_appname,
        "janis_branch": production_janis_branch
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "Can only deploy to production Janis from 'production' Publisher."


def test_deploy_to_prod_from_nonprod_joplin(patch_demo_table, mocker):
    # Sets is_production() validator to True
    mocker.patch('handlers.publish_request_handler.is_production', return_value=True)
    context = {}
    event = make_event({
        "joplin_appname": "pr-not-prod",
        "janis_branch": production_janis_branch
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f"Can only deploy to production Janis from {production_joplin_appname}."


def test_deploy_staging_to_wrong_janis(patch_demo_table, mocker):
    # Sets is_staging() validator to True
    mocker.patch('handlers.publish_request_handler.is_staging', return_value=True)
    context = {}
    event = make_event({
        "joplin_appname": staging_joplin_appname,
        "janis_branch": "not-staging-janis"
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "'staging' Publisher can only deploy to staging Janis."


def test_deploy_staging_to_wrong_janis(patch_demo_table, mocker):
    # Sets is_production() validator to True
    mocker.patch('handlers.publish_request_handler.is_production', return_value=True)
    context = {}
    event = make_event({
        "joplin_appname": production_joplin_appname,
        "janis_branch": "not-prod-janis"
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == "'production' Publisher can only deploy to production Janis."


@pytest.mark.parametrize("build_type", ["", "fake_build_type"])
def test_bad_build_types(patch_demo_table, build_type):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": build_type,
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'[{build_type}] is not a valid build_type.'


@pytest.mark.parametrize("pages", ["a string", {"a": "apple"}])
def test_pages_wrong_types(patch_demo_table, pages):
    context = {}
    event = make_event({
        "api_key": "dummy-api-key",
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "pages": pages
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'pages must be a list.'


@pytest.mark.parametrize("pages", [
    [{"id": 6, "author": ""}],
])
def test_pages_empty_strings(patch_demo_table, pages):
    context = {}
    event = make_event({
        "api_key": "dummy-api-key",
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "pages": pages
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'Empty strings are not allowed in pages.'


@pytest.mark.parametrize("pages", [
    [{"id": 6}],
])
def test_pages_missing_api_key(patch_demo_table, pages):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "pages": pages
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'api_key is required when updating specific pages'


def test_empty_pages_allows_missing_api_key(patch_demo_table):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "pages": []
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 200


@pytest.mark.parametrize("env_vars", ["a string", ["apple", "banana"]])
def test_env_vars_wrong_types(patch_demo_table, env_vars):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "env_vars": env_vars
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'env_vars must be a dict.'


# Don't allow empty string for any env_var
@pytest.mark.parametrize("env_var", [
    {f"{env_var}": ""} for env_var in valid_optional_env_vars
])
def test_env_vars_empty_string(patch_demo_table, env_var):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "env_vars": env_var
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'Empty strings are not allowed in env_vars.'


# Don't accept non-whitelisted env_vars
@pytest.mark.parametrize("env_var", [
    "invalid_env_var"
])
def test_invalid_env_var(patch_demo_table, env_var):
    context = {}
    event = make_event({
        "joplin_appname": "pytest",
        "janis_branch": "pytest",
        "build_type": "rebuild",
        "env_vars": {
            f"{env_var}": "value"
        }
    })
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 422
    res_body = json.loads(res["body"])
    assert res_body["message"] == f'env_var {env_var} is not a valid_optional_env_var.'


build_type_vals = ["rebuild", "incremental", "all_pages"]
janis_vals = ["pytest", "also-pytest"]
joplin_vals = ["pytest", "also-pytest"]
env_vars_vals = [
    None,
    {},
    {"REACT_STATIC_PREFETCH_RATE": 0},
    {"REACT_STATIC_PREFETCH_RATE": 10},
]
pages_vals = [
    None,
    [],
    [
        {
            "id": 101,
            "global_id": 'b2ZmaWNpYWxfZG9jdW1lbnQ6MTAx',
            "triggered_build": True,
            "action": "publish",
            "is_page": True,
            "content_type": "official_documents",
            "author": 3
        },
        {
            "id": 102,
            "global_id": 'c2VydmljZV9wYWdlOjEwMg==',
            "triggered_build": False,
            "action": "publish",
            "is_page": True,
            "content_type": "service_page",
            "author": 3
        }
    ]
]
all_combinations = []
for build_type in build_type_vals:
    for janis in janis_vals:
        for joplin_appname in joplin_vals:
            for env_vars in env_vars_vals:
                for pages in pages_vals:
                    all_combinations.append({
                        "api_key": "dummy-api-key",
                        "build_type": build_type,
                        "janis_branch": janis,
                        "joplin_appname": joplin_appname,
                        "env_vars": env_vars,
                        "pages": pages,
                    })
@pytest.mark.parametrize("data", all_combinations)
def test_valid_publish_requests(patch_demo_table, dynamodb_table, data):
    context = {}
    event = make_event(data)
    res = publish_request_handler(event, context)
    assert res["statusCode"] == 200

    # Check that REQ item exists and contains expected data
    res_body = json.loads(res["body"])
    pk = res_body["pk"]
    sk = res_body["sk"]
    request_item = dynamodb_table.get_item(
        Key={"pk": pk, "sk": sk},
        ProjectionExpression='build_id, #s, pages, joplin, env_vars, build_type',
        ExpressionAttributeNames={
            "#s": "status"
        }
    )['Item']

    expected_joplin = data['joplin_appname']
    assert request_item['joplin'] == expected_joplin

    expected_build_type = data['build_type']
    assert request_item['build_type'] == expected_build_type

    expected_pages = data['pages']
    if expected_pages is None:
        # publish_request_handler should default pages to []
        expected_pages = []
    # publish_request_handler adds a timestamp for each page.
    # This helps order page requests when they get consolidated into a single BLD item.
    for page in expected_pages:
        page["timestamp"] = sk
    assert request_item['pages'] == expected_pages

    expected_env_vars = data['env_vars']
    if expected_env_vars is None:
        # publish_request_handler should default env_vars to {}
        expected_env_vars = {}
    assert request_item['env_vars'] == expected_env_vars

    expected_status = f'waiting#{sk}'
    assert request_item['status'] == expected_status
