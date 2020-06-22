from os import path
import sys
sys.path.append(path.join(path.dirname(__file__), '../handlers'))

import os, json
from commands.process_new_build import process_new_build

process_new_build("BLD#build-search#2020-05-04T14:10:58.133084-05:00", {})
