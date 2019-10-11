from flask import Blueprint, request
import os, json, requests

from helpers.res_handlers import handle_missing_arg, handle_success

bp = Blueprint('publish', __name__)

@bp.route('/', methods=('POST',))
def publish():
    data = request.get_json(force=True)

    # Get Mandatory Args
    janis_branch = data.get('janis_branch')
    if not janis_branch:
        return handle_missing_arg('janis_branch')

    CMS_API = data.get('CMS_API')
    if not CMS_API:
        return handle_missing_arg('CMS_API')

    # Get Optional Args
    CMS_MEDIA = data.get('CMS_MEDIA')
    CMS_DOCS = data.get('CMS_DOCS')

    return handle_success(f"janis_branch is {janis_branch} and CMS_API is {CMS_API}")
