import numpy as np
from copy import deepcopy
from typing import Union, Optional, Any, NoReturn

from easyInterface.Utils.units import Unit
from easyInterface.Utils.DictTools import PathDict, UndoableDict
from easyInterface.Utils.Logging import logging
from easyInterface import logger, VERBOSE
from abc import abstractmethod


class LoggedClasses:

    def __init__(self):
        pass

    def __deepcopy__(self, memo):
        """
        We can't deepcopy log objects on python 3.6 :-(
        :param memo:
        :return:
        """
        cls = self.__class__
        newobj = cls.__new__(cls)
        memo[id(self)] = newobj
        log_key = None
        for k, v in self.__dict__.items():
            if isinstance(v, logging.Logger):
                log_key = k
                continue
            setattr(newobj, k, deepcopy(v, memo))
        if log_key is not None:
            setattr(newobj, log_key, logging.getLogger(self.__class__.__module__))
        return newobj


class LoggedUndoableDict(LoggedClasses, UndoableDict):

    def __init__(self, *args, **kwargs):
        LoggedClasses.__init__(self)
        UndoableDict.__init__(self, *args, **kwargs)


class LoggedPathDict(LoggedClasses, PathDict):

    def __init__(self, *args, **kwargs):
        LoggedClasses.__init__(self)
        PathDict.__init__(self, *args, **kwargs)


class ContainerObj(LoggedPathDict):
    """
    Container for multiple objects
    """

    def __init__(self, objs, in_type, identifier: str = 'name'):
        """
        Constructor for holding multiple objects
        :param objs: A collection of PathDict based objects
        :param in_type: The type of a single object
        :param identifier: Some objects are not referenced by name. I.e `site_label` for atoms
        """
        if isinstance(objs, in_type):
            objs = {
                objs[identifier]: objs,
            }
        if isinstance(objs, list):
            these_objs = dict()
            for obj in objs:
                these_objs[obj[identifier]] = obj
            objs = these_objs
        super().__init__(**objs)

    @abstractmethod
    def __repr__(self) -> str:
        return ''

    def getNames(self) -> list:
        return list(self.keys())


class Data(LoggedPathDict):
    """
    Data class which contains the value, error, constraint, hidden and refine attributes
    """

    def __init__(self, value: Optional[Any] = None, unit: Optional[Union[str, Unit]] = ''):
        """
        Create a data class from a value with a unit. Can be left blank
        :param value: default value for the data
        :param unit: default unit for the data in the form of a easyInterface.Untils.unit
        """
        if not isinstance(unit, Unit):
            # Try to convert the unit to a string
            unit = Unit(unit)
        super().__init__(value=value, unit=unit, min=-np.Inf, max=np.Inf, error=0, constraint=None, hide=True, refine=False)
        self._log = logger.getLogger(__class__.__module__)

    def __repr__(self) -> str:
        return '{}'.format(self['value'])

    @property
    def min(self) -> float:
        return self['min']

    @min.setter
    def min(self, value):
        self['min'] = value

    @property
    def max(self) -> float:
        return self['max']

    @max.setter
    def max(self, value):
        self['max'] = value

class Base(LoggedPathDict):
    def __init__(self, value: object = None, unit: object = '') -> object:
        super().__init__(header='Undefined', tooltip='', url='', mapping=None, store=Data(value, unit))
        self._log = logger.getLogger(__class__.__module__)
        self.updateMinMax()

    def __repr__(self) -> str:
        return '{} {}'.format(self.value, self.getItemByPath(['store', 'unit']))

    def updateMinMax(self):
        if not isinstance(self.value, (int, float)):
            return
        # unstacked changes (for initial min and max values)
        if self.min == -np.Inf:
            if np.isclose([self.value], [0]):
                self['store'].min = -1
            elif self.value > 0:
                self['store'].min = 0.8*self.value
            elif self.value < 0:
                self['store'].min = 1.2*self.value
        if self.max == np.Inf:
            if np.isclose([self.value], [0]):
                self['store'].max = 1
            elif self.value > 0:
                self['store'].max = 1.2*self.value
            elif self.value < 0:
                self['store'].max = 0.8*self.value

    @property
    def value(self) -> Any:
        return self.getItemByPath(['store', 'value'])

    @value.setter
    def value(self, value: Any) -> NoReturn:
        self.setItemByPath(['store', 'value'], value)

    @property
    def refine(self) -> bool:
        return self.getItemByPath(['store', 'refine'])

    @refine.setter
    def refine(self, value: bool) -> NoReturn:
        self.setItemByPath(['store', 'refine'], value)

    def get(self, item: str) -> Any:
        return self.getItemByPath(['store', item])

    def set(self, item: str, value: Any) -> NoReturn:
        self.setItemByPath(['store', item], value)

    def unitConversionFactor(self, newUnit: str) -> float:
        if self.getItemByPath(['store', 'unit']) is None:
            return 1
        return self.getItemByPath(['store', 'unit']).get_conversion_factor(newUnit)

    def convertUnits(self, newUnit: str) -> NoReturn:
        cf = self.unitConversionFactor(newUnit)
        self.setItemByPath(['store', 'value'], cf * self.value)
        self.setItemByPath(['store', 'unit'], Unit(newUnit))

    def valueInUnit(self, newUnit: str) -> float:
        cf = self.unitConversionFactor(newUnit)
        return cf * self.value

    @property
    def min(self) -> float:
        return self.getItemByPath(['store', 'min'])

    @min.setter
    def min(self, value):
        self.setItemByPath(['store', 'min'], value)

    @property
    def max(self) -> float:
        return self.getItemByPath(['store', 'max'])

    @max.setter
    def max(self, value):
        self.setItemByPath(['store', 'max'], value)
