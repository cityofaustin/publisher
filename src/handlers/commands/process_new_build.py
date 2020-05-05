from commands.start_janis_builder_factory import start_janis_builder_factory
from commands.run_janis_builder_task import run_janis_builder_task
from commands.process_build_failure import process_build_failure
from helpers.utils import get_build_item, get_latest_task_definition, get_janis_branch
import helpers.stages as stages


def process_new_build(build_id, context):
    try:
        print(f'##### New build request submitted [{build_id}].')

        # Get BLD data
        janis_branch = get_janis_branch(build_id)
        build_item = get_build_item(build_id)
        if not build_item:
            return None

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
            # If a janis_builder task_definition exists for your janis_branch, then run it
            latest_task_definition = get_latest_task_definition(janis_branch)
            if latest_task_definition:
                run_janis_builder_task(build_item, latest_task_definition)
            # Otherwise, you'll need to run the janis_builder_factory to create and register a janis_builder task
            else:
                print(f'##### No latest_task_definition found for [{janis_branch}]. Starting janis_builder_factory.')
                start_janis_builder_factory(build_id)
    except Exception as error:
        import traceback
        print(traceback.format_exc())
        process_build_failure(build_id, context)
