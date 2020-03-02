#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 01/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.10'

from abc import abstractmethod
from copy import deepcopy
from typing import Union, Optional, Any, NoReturn, Callable

from easyInterface import VERBOSE
from easyInterface.Utils.Depreciated import deprecated_function
from easyInterface.Utils.DictTools import PathDict, UndoableDict
from easyInterface.Utils.Logging import logging
from easyInterface.Utils.units import Unit, FloatWithUnit


class LoggedClasses:
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


class ParContainer(LoggedPathDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = None
        for key in kwargs.keys():
            if isinstance(self[key], Parameter):
                setattr(self.__class__, key, property(self.__gitem(key)))
            else:
                setattr(self.__class__, key, property(self.__gitem(key), self.__sitem(key)))

    def __setitem__(self, key, value):
        if key in self.keys():
            if isinstance(self[key], Parameter):
                self[key].value = value
                return
        super().__setitem__(key, value)

    @staticmethod
    def __gitem(key: str) -> Callable:
        def inner(obj):
            try:
                data = obj[key]
                return data
            except KeyError:
                raise AttributeError

        return lambda obj: inner(obj)

    @staticmethod
    def __sitem(key):
        return lambda obj, value: obj.__setitem__(key, value)


class Parameter:
    def __init__(self, value, unit, **kwargs):
        self._value = FloatWithUnit(value, unit)
        self.__properties = kwargs
        self.fittable = False
        self.error = None
        self.hidden = False
        self.constraint = lambda x: True
        self.max_min_scale = 0.2
        for key in self.__properties.keys():
            setattr(self.__class__, key, property(self.__gitem(key)))

    def __repr__(self):
        return self._value.__repr__()

    def __str__(self):
        base = self._value.__repr__()
        if self.error is not None:
            base += ' \u00B1 {}'.format(self.error)
        if self._value.unit is not None:
            base += ' {}'.format(self._value.unit)
        return base

    def modify_meta_data(self, key, value):
        self.__properties[key] = value

    @property
    def unit(self) -> Unit:
        return self.value.unit

    @unit.setter
    def unit(self, new_unit: str):
        factor = self._value.unit.get_conversion_factor(new_unit)
        self._value = FloatWithUnit(self._value * factor, new_unit, unit_type=self._value.unit_type)

    @property
    def max(self):
        return FloatWithUnit(self._value * (1 + self.max_min_scale), self._value.unit, unit_type=self._value.unit_type)

    @property
    def min(self):
        return FloatWithUnit(self._value * (1 - self.max_min_scale), self._value.unit, unit_type=self._value.unit_type)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.constraint(value):
            self._value = FloatWithUnit(value, self._value.unit, unit_type=self._value.unit_type)
        else:
            raise ValueError('The supplied value fails validation')

    @staticmethod
    def __gitem(key: str) -> Callable:
        def inner(obj):
            try:
                data = obj.__properties[key]
                return data
            except KeyError:
                raise AttributeError

        return lambda obj: inner(obj)


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
        super().__init__(value=value, unit=unit, error=0, constraint=None, hide=True, refine=False)
        self._log = logging.getLogger(__name__)
        self._log.log(VERBOSE, 'Data object created with default value %s, unit %s', value, unit)

    def __repr__(self) -> str:
        return '{}'.format(self['value'])

    @property
    def min(self) -> float:
        value = self['value']
        ret = None
        if value is not None:
            if isinstance(value, (int, float, complex)) and not isinstance(value, bool):
                ret = 0.8 * self['value']
        return ret

    @property
    def max(self) -> float:
        value = self['value']
        ret = None
        if value is not None:
            if isinstance(value, (int, float, complex)) and not isinstance(value, bool):
                ret = 1.2 * self['value']
        return ret


class Base(LoggedPathDict):
    def __init__(self, value: object = None, unit: object = '') -> object:
        super().__init__(header='Undefined', tooltip='', url='', mapping=None, store=Data(value, unit))

    def __repr__(self) -> str:
        return '{} {}'.format(self.value, self.getItemByPath(['store', 'unit']))

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
