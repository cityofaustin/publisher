import os
from start_janis_builder_factory import start_janis_builder_factory

start_janis_builder_factory(os.getenv("JANIS_BRANCH"), os.getenv("DEST"))
