#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 01/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.8'


from easyInterface.Utils.Depreciated import deprecated
from easyInterface.Common.PhaseObj.Lattice import *

new_class = 'easyInterface.Common.PhaseObj.Lattice'
CELL_DETAILS = LATTICE_DETAILS


class Cell(Lattice):
    """
    Container for crystallographic unit cell parameters
    """

    @deprecated(new_class)
    def __init__(self, *args, **kwargs):
        """
        Constructor for the crystallographic unit cell

        :param length_a: Unit cell length a
        :param length_b: Unit cell length b
        :param length_c:  Unit cell length c
        :param angle_alpha: Unit cell angle alpha
        :param angle_beta:  Unit cell angle beta
        :param angle_gamma:  Unit cell angle gamma
        """
        super().__init__(*args, **kwargs)

    @classmethod
    @deprecated(new_class + '.default()')
    def default(cls) -> Lattice:
        """
        Default constructor for a crystallographic unit cell

        :return: Default crystolographic unit cell container
        """
        return super().default()

    @classmethod
    @deprecated(new_class + '.fromPars()')
    def fromPars(cls, *args, **kwargs) -> Lattice:
        """
        Constructor of a crystallographic unit cell when parameters are known

        :param length_a: Unit cell length a
        :param length_b: Unit cell length b
        :param length_c:  Unit cell length c
        :param angle_alpha: Unit cell angle alpha
        :param angle_beta:  Unit cell angle beta
        :param angle_gamma:  Unit cell angle gamma
        :return:
        """
        return super().fromPars(*args, **kwargs)
