import os
from start_janis_builder_factory import start_janis_builder_factory
from register_janis_builder_task import register_janis_builder_task

# start_janis_builder_factory(os.getenv("JANIS_BRANCH"), os.getenv("DEST"))
register_janis_builder_task(os.getenv("JANIS_BRANCH"))
