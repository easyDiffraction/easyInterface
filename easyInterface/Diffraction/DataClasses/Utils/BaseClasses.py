from typing import Union, Optional, Any, NoReturn

from easyInterface.Utils.units import Unit
from easyInterface.Utils.DictTools import PathDict
from easyInterface.Utils.Logging import logging
from easyInterface import VERBOSE
from abc import abstractmethod


class ContainerObj(PathDict):
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


class Data(PathDict):
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


class Base(PathDict):
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
