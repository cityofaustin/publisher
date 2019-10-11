from flask import Blueprint, request
import os, json, requests

from pprint import pprint

from helpers.res_handlers import handle_400_error, handle_missing_arg, handle_success
from helpers.validate_janis_branch import validate_janis_branch

bp = Blueprint('build', __name__)

@bp.route('/', methods=('POST',))
def build():
    data = request.get_json(force=True)

    netlify_env = {}

    # Get Mandatory Args
    janis_branch = data.get('janis_branch')
    if not janis_branch:
        return handle_missing_arg('janis_branch')

    CMS_API = data.get('CMS_API')
    netlify_env["CMS_API"] = CMS_API
    if not CMS_API:
        return handle_missing_arg('CMS_API')

    # Get Optional Args
    CMS_MEDIA = data.get('CMS_MEDIA')
    if CMS_MEDIA: netlify_env["CMS_MEDIA"] = CMS_MEDIA
    CMS_DOCS = data.get('CMS_DOCS')
    if CMS_DOCS: netlify_env["CMS_DOCS"] = CMS_DOCS


    site_name = f'janis-{janis_branch}'
    netlify_url = "https://api.netlify.com/api/v1"
    netlify_headers = {
        "Authorization": f"Bearer {os.getenv('NETLIFY_AUTH_TOKEN')}",
        "Content-Type": "application/json",
    }

    # Get site_id if site already exists
    sites = requests.get(
        url=netlify_url+"/sites",
        headers=netlify_headers,
    ).json()

    site_id = None
    site_url = None
    prior_site = False
    for x in sites:
        if x["name"] == site_name:
            site_id = x["site_id"]
            site_url = x["url"]
            prior_site = True
            print(f"Found an existing site for {site_name}")
            break

    # Make a netlify site for the branch if it doesn't already exist
    if not site_id:
        print(f"Building a new site for {site_name}")

        if not validate_janis_branch(janis_branch):
            return handle_400_error(f"[{janis_branch}] is not a valid janis_branch")

        site = requests.post(
            url=netlify_url+"/sites",
            data=json.dumps({
                "name": site_name,
                "repo": {
                    "provider": "github",
                    "repo": "cityofaustin/janis",
                    "private": False,
                    "branch": janis_branch,
                    "cmd": "yarn publish-netlify-pr",
                    "dir": "dist",
                    "installation_id": int(os.getenv('NETLIFY_GITHUB_INSTALLATION_ID')),
                },
            }),
            headers=netlify_headers,
        ).json()

        site_id = site["site_id"]
        site_url = site["url"]

        # Only PUT requests can set the "skip_pr" setting
        put_res = requests.put(
            url=f"{netlify_url}/sites/{site_id}",
            data=json.dumps({
                "build_settings": {
                    "skip_prs": True,
                    "env": netlify_env,
                }
            }),
            headers=netlify_headers,
        ).json()

    # Create a build hook for the branch if it doesn't exist
    build_hooks = requests.get(
        url=f"{netlify_url}/sites/{site_id}/build_hooks",
        headers=netlify_headers,
    ).json()

    build_hook_url = None
    for x in build_hooks:
        if x["title"] == "PUBLISH":
            print(f"Found an existing build_hook for {site_name}")
            build_hook_url = x["url"]
            break

    if not build_hook_url:
        print(f"Building a new build_hook for {site_name}")
        build_hook_url = requests.post(
            url=f"{netlify_url}/sites/{site_id}/build_hooks",
            data=json.dumps({
                "title": "PUBLISH",
            }),
            headers=netlify_headers,
        ).json()["url"]

    if prior_site:
        return handle_success(f"Janis pr site for {janis_branch} already exists: {site_url}")

    return handle_success(f"Created Janis pr site for {janis_branch}")
