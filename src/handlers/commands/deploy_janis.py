import os

from helpers.netlify import (
    get_site_name,
    get_site,
    create_site,
    upload_janis_to_netlify
)
from helpers.utils import get_zipped_janis_build


def deploy_janis(janis_branch):
    '''
    If Review:
        - must be deployed on netlify
    If Staging:
        - must be deployed on AWS
        - CDN cache invalidation
    If prod:
        - must be deployed on AWS
        - CDN cache invalidation
    '''
    if os.getenv("DEPLOY_ENV") not in ("staging", "production"):
        netlify_site_name = get_site_name(janis_branch)
        netlify_site = get_site(netlify_site_name)
        if not netlify_site:
            netlify_site = create_site(netlify_site_name)
            if not netlify_site["id"]:
                raise Exception("Oh no")
        netlify_site_id = netlify_site["id"]
        zipped_janis_build = get_zipped_janis_build(janis_branch)
        res = upload_janis_to_netlify(netlify_site_id, zipped_janis_build)
        print("hi")
