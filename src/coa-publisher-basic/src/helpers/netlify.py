import os, json, requests
import urllib.parse

netlify_url = "https://api.netlify.com/api/v1"
netlify_headers = {
    "Authorization": f"Bearer {os.getenv('NETLIFY_AUTH_TOKEN')}",
    "Content-Type": "application/json",
}

# Get site if site already exists
def get_site(site_name):
    site = None
    more_sites = True
    pagination = 1
    while more_sites:
        # Paginated query to list netlify sites
        netlify_res = requests.get(
            url=f"{netlify_url}/sites?page={pagination}&per_page=100",
            headers=netlify_headers,
        )

        # Check if there is another page of branches to query
        netlify_res_link = requests.utils.parse_header_links(netlify_res.headers["link"])
        more_sites = False
        for x in netlify_res_link:
            if x["rel"] == "next":
                more_sites=True
                pagination=pagination+1
                break

        # Get site if site_name is among the queried sites
        sites = netlify_res.json()
        for x in sites:
            if x["name"] == site_name:
                site = x
                break

        # If site was found, break out of while loop
        # Else, the loop continues if there are more paginated results to be queried
        if site: break

    return site

# Create a new netlify site
# Returns site
def create_site(site_name, janis_branch):
    return requests.post(
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

# Only PUT requests (not POST requests) can set the "skip_pr" and "env" settings
def update_site(site_id, data):
    requests.put(
        url=f"{netlify_url}/sites/{site_id}",
        data=json.dumps(data),
        headers=netlify_headers,
    )

# Create incoming publish hook and outgoing github notification hooks
def create_hooks(site_id):
    # Create publish hook
    requests.post(
        url=f"{netlify_url}/sites/{site_id}/build_hooks",
        data=json.dumps({
            "title": "PUBLISH",
        }),
        headers=netlify_headers,
    )

    # Create outgoing github hooks
    github_hooks = [
        {
            "event": "deploy_building",
            "type": "github_app_commit_status"
        },
        {
            "event": "deploy_building",
            "type": "github_app_checks"
        },
        {
            "event": "deploy_created",
            "type": "github_app_commit_status"
        },
        {
            "event": "deploy_created",
            "type": "github_app_checks"
        },
        {
            "event": "deploy_failed",
            "type": "github_app_commit_status"
        },
        {
            "event": "deploy_failed",
            "type": "github_app_checks"
        }
    ]
    for hook in github_hooks:
        requests.post(
            url=f"{netlify_url}/hooks",
            data=json.dumps({
                "site_id": site_id,
                **hook
            }),
            headers=netlify_headers,
        )

# Get publish webhook for a netlify site
def get_publish_hook(site_id):
    publish_hook_url = None
    build_hooks = requests.get(
        url=f"{netlify_url}/sites/{site_id}/build_hooks",
        headers=netlify_headers,
    ).json()

    for x in build_hooks:
        if x["title"] == "PUBLISH":
            publish_hook_url = x["url"]
            break

    return publish_hook_url

# Triggers the publish_hook
# Future option: adding a data param will be passed through as "INCOMING_HOOK_BODY" env var
def run_publish_hook(publish_hook_url, CMS_API):
    requests.post(
        url=publish_hook_url,
        params={
            "trigger_title": f"triggered by publish from {urllib.parse.urlparse(CMS_API).netloc or CMS_API}"
        },
        headers=netlify_headers,
    )

# Could be used to check status of build created by create_build()
def check_build_status(site_id, deploy_id):
    deploy = requests.get(
        url=f"{netlify_url}/sites/{site_id}/deploys/{deploy_id}",
        headers=netlify_headers,
    ).json()

# Starts a build job in netlify
# Returns deploy_id, can be pinged to get status of a deploy, which is not possible with webhook invocation
def create_build(site_id):
    deploy_id = requests.post(
        url=f"{netlify_url}/sites/{site_id}/builds",
        headers=netlify_headers,
    ).json()["deploy_id"]

    return deploy_id
