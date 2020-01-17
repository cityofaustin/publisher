from flask import request

from app import app
from helpers.res_handlers import handle_error, handle_missing_arg, handle_success

'''
{
    janis_branch: (string),
        The name of the janis branch you want to build
    action: (string),
        "publish", "unpublish"
    page_ids: (array of strings),
    environment_vars: {
        CMS_API: (string),
            The Joplin /graphql endpoint used to source page data for your janis build
        CMS_MEDIA: (string),
            The location of the static images for you janis build
        CMS_DOCS: (string),
            The location of the documents for your janis build
        DEPLOYMENT_MODE: (string),
            "LOCAL", "REVIEW", "STAGING", "PRODUCTION"
            A flag to indicate the environment of the build
    }
}
'''
@app.route('/build', methods=('POST',), strict_slashes=False)
def build():
    data = request.get_json(force=True)
    janis_branch = data.get('janis_branch').lower()
