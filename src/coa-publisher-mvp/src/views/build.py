from flask import request

from app import app

from helpers.res_handlers import handle_error, handle_missing_arg, handle_success
from helpers.github import validate_janis_branch
from helpers.netlify import get_site, create_site, update_site, get_publish_hook, create_hooks

@app.route('/build', methods=('POST',), strict_slashes=False)
def build():
    data = request.get_json(force=True)
    netlify_env = {} # env vars to plug into netlify site
    # Handle janis_branch arg
    janis_branch = data.get('janis_branch').lower()
    if not janis_branch:
        return handle_missing_arg('janis_branch')
    site_name = f'janis-{janis_branch}'
    # Handle CMS_API arg
    CMS_API = data.get('CMS_API')
    netlify_env["CMS_API"] = CMS_API
    if not CMS_API:
        return handle_missing_arg('CMS_API')
    # Handle optional Args
    CMS_MEDIA = data.get('CMS_MEDIA')
    if CMS_MEDIA: netlify_env["CMS_MEDIA"] = CMS_MEDIA
    CMS_DOCS = data.get('CMS_DOCS')
    if CMS_DOCS: netlify_env["CMS_DOCS"] = CMS_DOCS
    DEPLOYMENT_MODE = data.get('DEPLOYMENT_MODE')
    if DEPLOYMENT_MODE: netlify_env["DEPLOYMENT_MODE"] = DEPLOYMENT_MODE

    # Create Site if it doesn't already exist
    site = get_site(site_name)

    if site:
        existing_site = True
        site_id = site["id"]
        site_url = site["url"]
        print(f"Found an existing site for {site_name}")
    else:
        existing_site = False
        # Make a netlify site for the branch if it doesn't already exist
        print(f"Building a new site for {site_name}")
        if not validate_janis_branch(janis_branch):
            return handle_error(f"[{janis_branch}] is not a valid janis_branch", 400)
        site = create_site(site_name, janis_branch, netlify_env)
        site_id = site["id"]
        site_url = site["url"]

    # Update values for site
    update_site(site_id, {
        "build_settings": {
            "skip_prs": True,
        }
    })

    # If there isn't a publish hook, assume that all hooks need to be built.
    publish_hook_url = get_publish_hook(site_id)
    if not publish_hook_url:
        create_hooks(site_id)

    # Return success message
    if existing_site:
        return handle_success(f"Janis pr site for {janis_branch} already exists: {site_url}")
    else:
        return handle_success(f"Created Janis pr site for {janis_branch}")
