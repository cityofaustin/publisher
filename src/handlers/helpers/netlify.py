import os, json, requests

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
        more_sites = False
        if netlify_res.headers.get("link"):
            netlify_res_link = requests.utils.parse_header_links(netlify_res.headers.get("link"))
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
def create_site(netlify_site_name):
    return requests.post(
        url=netlify_url+"/sites",
        data=json.dumps({
            "name": netlify_site_name,
        }),
        headers=netlify_headers,
    ).json()


def upload_janis_to_netlify(netlify_site_id, zipped_janis_build):
    upload_janis_headers = netlify_headers
    upload_janis_headers["Content-Type"] = "application/zip"
    return requests.post(
        url=f'{netlify_url}/sites/{netlify_site_id}/deploys',
        data=zipped_janis_build,
        headers=upload_janis_headers,
    ).json()


# Could be used to check status of build created by create_build()
def check_build_status(netlify_site_id, deploy_id):
    deploy = requests.get(
        url=f"{netlify_url}/sites/{netlify_site_id}/deploys/{deploy_id}",
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
