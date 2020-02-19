from helpers.utils import get_current_build_item
import helpers.stages as stages

from helpers.start_janis_builder_factory import start_janis_builder_factory


def process_new_build(janis_branch, context):
    print(f'##### New build request submitted for [{janis_branch}].')

    # Get BLD data
    build_item = get_current_build_item(janis_branch)
    if not build_item:
        return None
    build_id = build_item["build_id"]

    # Skip if we've already processed this BLD already
    build_stage = build_item["stage"]
    if build_stage != stages.preparing_to_build:
        print(f'##### Build [{build_id}] already started')
        return None

    # Start a build, based on your BLD's build_type
    build_type = build_item["build_type"]
    if build_type == "rebuild":
        start_janis_builder_factory(build_id)
    else:
        print("##### skipping for now.")
        # We need to run task
        # If task doesn't exist, then start_janis_builder_factory
