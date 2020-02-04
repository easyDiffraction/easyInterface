import logging

VERBOSE = 5
logging.addLevelName(5, "verbose")

LEVEL = logging.INFO
FORMAT = "\033[1;32;49m%(asctime)s  |  %(name)s — %(levelname)s | %(lineno)-4d |  %(funcName)-5s  |  %(" \
         "message)s\033[0m "

from easyInterface.Diffraction.DataClasses import *
from easyInterface.Utils import *
from easyInterface.Utils.Logging import Logger


logger = Logger(level=LEVEL)
