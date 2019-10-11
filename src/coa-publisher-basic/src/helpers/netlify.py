import os, json, requests

netlify_url = "https://api.netlify.com/api/v1"
netlify_headers = {
    "Authorization": f"Bearer {os.getenv('NETLIFY_AUTH_TOKEN')}",
    "Content-Type": "application/json",
}

# Get site_id and site_url if site already exists
def get_site(site_name):
    site_id = None
    site_url = None

    sites = requests.get(
        url=netlify_url+"/sites",
        headers=netlify_headers,
    ).json()

    for x in sites:
        if x["name"] == site_name:
            site_id = x["site_id"]
            site_url = x["url"]
            break

    return site_id, site_url

# Create a new netlify site
def create_site(site_name, janis_branch, netlify_env):
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

    # Only PUT requests can set the "skip_pr" and "env" settings
    requests.put(
        url=f"{netlify_url}/sites/{site_id}",
        data=json.dumps({
            "build_settings": {
                "skip_prs": True,
                "env": netlify_env,
            }
        }),
        headers=netlify_headers,
    ).json()

    return site_id, site_url

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

# Create a publish webhook for a netlify site
def create_publish_hook(site_id):
    return requests.post(
        url=f"{netlify_url}/sites/{site_id}/build_hooks",
        data=json.dumps({
            "title": "PUBLISH",
        }),
        headers=netlify_headers,
    ).json()["url"]
