from os import path
import sys
sys.path.append(path.join(path.dirname(__file__), '..'))

import os, json
from handlers.commands.build_start import build_start

build_start(os.getenv("JANIS_BRANCH"))
