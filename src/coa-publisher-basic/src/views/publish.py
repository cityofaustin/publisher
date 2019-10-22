from flask import Blueprint, request

from app import app

from helpers.res_handlers import handle_error, handle_missing_arg, handle_success
from helpers.netlify import get_site, update_site, get_publish_hook, run_publish_hook

@app.route('/publish', methods=('POST',), strict_slashes=False)
def publish():
    data = request.get_json(force=True)
    # Handle janis_branch arg
    janis_branch = data.get('janis_branch')
    if not janis_branch:
        return handle_missing_arg('janis_branch')
    site_name = f'janis-{janis_branch}' # name of the netlify site
    # Handle CMS_API arg
    CMS_API = data.get('CMS_API')
    if not CMS_API:
        return handle_missing_arg('CMS_API')
    # Handle optional Args
    CMS_MEDIA = data.get('CMS_MEDIA')
    CMS_DOCS = data.get('CMS_DOCS')
    FEEDBACK_API = data.get('FEEDBACK_API')

    # Get netlify site data
    site = get_site(site_name)
    if not site:
        return handle_error(f"janis_branch [{janis_branch}] has not been deployed to netlify.", 400)
    site_id = site["id"]
    site_url = site["url"]

    # Update site with new env variable values
    netlify_env = site["build_settings"]["env"]
    netlify_env["CMS_API"] = CMS_API
    if CMS_MEDIA: netlify_env["CMS_MEDIA"] = CMS_MEDIA
    if CMS_DOCS: netlify_env["CMS_DOCS"] = CMS_DOCS
    if FEEDBACK_API: netlify_env["FEEDBACK_API"] = FEEDBACK_API
    update_site(site_id, {
        "build_settings": {
            "env": netlify_env,
        }
    })

    # Run publish_hook
    publish_hook_url = get_publish_hook(site_id)
    if not publish_hook_url:
        return handle_error(f"Could not find a publish_hook for site [{site_name}].", 404)
    run_publish_hook(publish_hook_url, CMS_API)

    return handle_success(f"janis_branch is {janis_branch} and CMS_API is {CMS_API}")
