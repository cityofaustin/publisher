import os, json, requests, hashlib
from pprint import pprint

site_name = f'janis-{os.getenv("JANIS_BRANCH")}'
netlify_url = "https://api.netlify.com/api/v1"
headers = {
    "Authorization": f"Bearer {os.getenv('NETLIFY_AUTH_TOKEN')}",
    "Content-Type": "application/json",
}

# Get site_id if site already exists
sites = requests.get(
    url=netlify_url+"/sites",
    headers=headers,
).json()

site_id = None
for x in sites:
    if x["name"] == site_name:
        print("~~~ Found an existing site")
        site_id = x["site_id"]
        break

# Make a netlify site for the branch if it doesn't already exist
if not site_id:
    site_id = requests.post(
        url=netlify_url+"/sites",
        data=json.dumps({
            "name": site_name,
            "repo": {
                "provider": "github",
                "repo": "cityofaustin/janis",
                "private": "false",
                "branch": os.getenv("JANIS_BRANCH"),
                "cmd": "yarn build-joplin-cloud",
                "dir": "dist"
            },
            "build_settings": {
                "skip_prs": "true"
            }
        }),
        headers=headers,
    ).json()['site_id']

    # Only PUT requests can set the "skip_pr" setting
    put_res = requests.put(
        url=f"{netlify_url}/sites/{site_id}",
        data=json.dumps({
            "build_settings": {
                "skip_prs": "true"
            }
        }),
        headers=headers,
    ).json()

print(f"~~~~ site_id is {site_id}")


# Create a build hook for the branch if it doesn't exist
build_hooks = requests.get(
    url=f"{netlify_url}/sites/{site_id}/build_hooks",
    headers=headers,
).json()

build_hook_url = None
for x in build_hooks:
    if x["title"] == "PUBLISH":
        print("~~~ Found an existing build_hook")
        build_hook_url = x["url"]
        break

if not build_hook_url:
    print("~~~ Building a new build_hook")
    build_hook_url = requests.post(
        url=f"{netlify_url}/sites/{site_id}/build_hooks",
        data=json.dumps({
            "title": "PUBLISH",
        }),
        headers=headers,
    ).json()["url"]

print(f"~~ Our build_hook_url: {build_hook_url}")

# Create a site deploy
data = {
    "async": "true",
    "files": {
        "/index.html": "907d14fb3af2b0d4f18c2d46abe8aedce17367bd",
    },
}
