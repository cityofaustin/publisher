import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from start_janis_builder_factory import start_janis_builder_factory
from register_janis_builder_task import register_janis_builder_task
from run_janis_builder_task import run_janis_builder_task

start_janis_builder_factory(os.getenv("JANIS_BRANCH"), os.getenv("DEST"))
# register_janis_builder_task(os.getenv("JANIS_BRANCH"))
# run_janis_builder_task(os.getenv("JANIS_BRANCH"))
