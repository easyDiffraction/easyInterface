import logging

# Default logging level
LEVEL = logging.INFO

# Logging format
FORMAT = "\033[1;32;49m%(asctime)s  |  %(name)s — %(levelname)s | %(lineno)-4d |  %(funcName)-5s  |  %(" \
         "message)s\033[0m "

# Add a logging level
VERBOSE = 5
logging.addLevelName(5, "verbose")

# Create the master logger
from easyInterface.Utils.Logging import Logger
logger = Logger(level=LEVEL)

# Create a logging object on initialisation 
from easyInterface.Diffraction.DataClasses import *
from easyInterface.Utils import *


