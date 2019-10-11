from flask import Blueprint, request

from helpers.res_handlers import handle_400_error, handle_missing_arg, handle_success
from helpers.github import validate_janis_branch
from helpers.netlify import get_site, create_site, get_publish_hook, create_publish_hook

bp = Blueprint('build', __name__)

@bp.route('/', methods=('POST',))
def build():
    data = request.get_json(force=True)

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

    # Initialize variables
    site_name = f'janis-{janis_branch}'
    netlify_env = {}
    existing_site = False

    ######
    # Begin
    ######

    site_id, site_url = get_site(site_name)

    if site_id:
        existing_site = True
        print(f"Found an existing site for {site_name}")
    else:
        # Make a netlify site for the branch if it doesn't already exist
        print(f"Building a new site for {site_name}")

        if not validate_janis_branch(janis_branch):
            return handle_400_error(f"[{janis_branch}] is not a valid janis_branch")

        site_id, site_url = create_site(site_name, janis_branch, netlify_env)

    publish_hook_url = get_publish_hook(site_id)

    # Create a build hook for the branch if it doesn't exist
    if not publish_hook_url:
        print(f"Building a new build_hook for {site_name}")
        publish_hook_url = create_publish_hook(site_id)

    if existing_site:
        return handle_success(f"Janis pr site for {janis_branch} already exists: {site_url}")

    return handle_success(f"Created Janis pr site for {janis_branch}")
