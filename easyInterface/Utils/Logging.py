#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 04/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.3'

import sys
from typing import Union

from easyInterface import LEVEL, FORMAT, logging


class Blacklist(logging.Filter):
    """
    Remove item/items from the log handler
    """
    def __init__(self, *blacklist):
        super().__init__()
        self.blacklist = [logging.Filter(name) for name in blacklist]

    def filter(self, record):
        return not any(f.filter(record) for f in self.blacklist)


class Whitelist(logging.Filter):
    """
    Allow only item/items from the log handler
    """
    def __init__(self, *whitelist):
        super().__init__()
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)


class Logger:
    """
    Enhancement of the default logger
    """
    def __init__(self, level=LEVEL, log_format=FORMAT):
        """
        Creator for the base logger. This should be called at __init__
        :param level: the default logging level
        :param log_format: the default log format
        """
        self.FORMAT = log_format
        self.LEVEL = level
        self.logging_level = level
        self.output_format = self._makeColorText()
        self._handlers = dict(sys=[], file=[])
        self._loggers = []
        self._filters = []

        # Gets or creates a logger
        self.logger = logging.getLogger(__name__)

        self._loggers.append(self.logger)

        # set log level
        self.setLevel(self.logging_level)

    def _makeColorText(self, color: str = '32'):
        return self.FORMAT.format(color)

    def setLevel(self, level):
        """
        Change the base logging level
        :param level: logging level
        :return: None
        """
        self.logging_level = level
        self.applyLevel()

    def applyLevel(self, loggers: Union[None, 'logging', list] = None):
        """
        Apply a logging level to a single logger or all loggers
        :param loggers: loggger - single logger, None - all logers, list - selected loggers
        :return: None
        """
        if loggers is None:
            loggers = self._loggers
        elif not isinstance(loggers, list):
            loggers = [loggers]

        for logger in loggers:
            logger.setLevel(self.logging_level)

    def addSysOutput(self):
        """
        Attach a terminal output for all loggers
        :return: None
        """
        if len(self._handlers['sys']) == 0:
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(self.output_format)
            console_handler.setFormatter(formatter)
            self._handlers['sys'].append(console_handler)
        for logger in self._loggers:
            logger.addHandler(self._handlers['sys'][0])

    def addFileHandler(self, location: str):
        """
        Attach a file output for all loggers
        :param location: string - Where should the logfile be saved
        :return: None
        """
        # define file handler and set formatter
        file_handler = logging.FileHandler(location)
        formatter = logging.Formatter(self.output_format)
        file_handler.setFormatter(formatter)
        self._handlers['file'].append(file_handler)
        # add file handler to logger
        for logger in self._loggers:
            logger.addHandler(file_handler)

    def removeFileHandlers(self):
        """
        Remove all file output from all loggers
        :return: None
        """
        for handler in self._handlers['file']:
            for logger in self._loggers:
                logger.removeHandler(handler)
        self._handlers['file'] = []

    def addNameFilter(self, *name: str):
        """
        Only log information corresponding to a name /names
        :param name: one or more names to log
        :return: None
        """
        filter = Whitelist(*name)
        self._filters.append(filter)
        for handler_type in self._handlers:
            for handler in self._handlers[handler_type]:
                handler.addFilter(filter)

    def addNameBlacklistFilter(self, *name: str):
        """
        Remove a log from the global log accorging to names
        :param name: one or more names not to log
        :return: None
        """
        filter = Blacklist(*name)
        self._filters.append(filter)
        for handler_type in self._handlers:
            for handler in self._handlers[handler_type]:
                handler.addFilter(filter)

    def getHandlers(self, log_type: str = 'file') -> list:
        """
        Get all of the handlers associated to logging according to type
        :param log_type: 'sys' or 'file'
        :return: list of log handlers
        """
        if log_type in self._handlers.keys():
            return self._handlers[log_type]

    def getLogger(self, logger_name, color: str = '32', defaults: bool = True) -> logging:
        """
        Create a logger
        :param color:
        :param logger_name: logger name. Usually __name__ on creation
        :param defaults: Do you want to associate any current file loggers with this logger
        :return: A logger
        """
        logger = logging.getLogger(logger_name)
        self.applyLevel(logger)
        for handler_type in self._handlers:
            for handler in self._handlers[handler_type]:
                if handler_type == 'sys' or defaults:
                    handler.formatter._fmt = self._makeColorText(color)
                    logger.addHandler(handler)
        logger.propagate = False
        self._loggers.append(logger)
        return logger