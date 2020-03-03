__author__ = 'andrewszonov'
__version__ = "2020_03_03"

from dicttoxml import dicttoxml
from easyInterface.Utils.Logging import Logger
from PySide2.QtCore import QObject, Slot

class QtLogger(QObject):
    def __init__(self, logger: Logger, parent=None):
        super().__init__(parent)
        self.__logger = logger
        self.__initial_level = logger.logging_level
        self.__levels = [
            { 'level': { 'name': 'Disabled', 'code': 0  } },
            { 'level': { 'name': 'Debug',    'code': 10 } },
            { 'level': { 'name': 'Info',     'code': 20 } },
            { 'level': { 'name': 'Warning',  'code': 30 } },
            { 'level': { 'name': 'Error',    'code': 40 } },
            { 'level': { 'name': 'Critical', 'code': 50 } }
        ]

    @Slot(int)
    def setLevel(self, index):
        level = self.__levels[index]['level']['code']
        self.__logger.setLevel(level)

    @Slot(result=str)
    def levelsAsXml(self):
        xml = dicttoxml(self.__levels, attr_type=False)
        xml = xml.decode()
        return xml

    @Slot(result=int)
    def defaultLevelIndex(self):
        for index, level in enumerate(self.__levels):
            if level['level']['code'] == self.__initial_level:
                return index
        return 0
