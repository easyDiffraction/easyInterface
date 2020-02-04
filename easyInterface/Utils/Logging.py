import sys
from easyInterface import LEVEL, FORMAT, logging


class Logger:

    def __init__(self, level=LEVEL, log_format=FORMAT):
        self.logging_level = level
        self.output_format = log_format

        Logger.LEVEL = level
        Logger.FORMAT = log_format

        # Gets or creates a logger
        self.logger = logging.getLogger(__name__)

        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(self.output_format)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # set log level
        self.setLevel(self.logging_level)

    def setLevel(self, level):
        self.logging_level = level
        self.logger.setLevel(self.logging_level)

    def logTo(self, location):
        # define file handler and set formatter
        file_handler = logging.FileHandler(location)
        formatter = logging.Formatter(self.output_format)
        file_handler.setFormatter(formatter)
        # add file handler to logger
        self.logger.addHandler(file_handler)

    @classmethod
    def getLogger(cls, logger_name, level=None, log_format=None) -> logging:
        logger = logging.getLogger(logger_name)
        if level is None:
            level = LEVEL
        if log_format is None:
            log_format = FORMAT
        logger.setLevel(level)  # better to have too much log than not enough
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.propagate = False
        return logger
