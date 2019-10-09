import os, json, requests, hashlib
from pprint import pprint

janis_branch = os.getenv("JANIS_BRANCH")
joplin_branch = os.getenv("JOPLIN_BRANCH")

site_name = f'janis-{janis_branch}-33'
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
                "private": False,
                "branch": janis_branch,
                "cmd": "yarn publish-netlify-pr",
                "dir": "dist",
                "installation_id": int(os.getenv('NETLIFY_GITHUB_INSTALLATION_ID')),
            },
        }),
        headers=headers,
    ).json()['site_id']

    # Only PUT requests can set the "skip_pr" setting
    put_res = requests.put(
        url=f"{netlify_url}/sites/{site_id}",
        data=json.dumps({
            "build_settings": {
                "skip_prs": True,
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

print("~~~ Running the build_hook!")

# Trigger the build hook
requests.post(
    url=build_hook_url,
    params={
        "trigger_branch": janis_branch,
        "trigger_title": f"triggered by publish from {joplin_branch}"
    },
    data=json.dumps({
        "name": "derpderp",
    }),
    headers=headers,
)
