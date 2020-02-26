#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 26/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


from easyInterface import logger as logging
from easyInterface.Common.Utils.BaseClasses import Base, LoggedPathDict

LATTICE_DETAILS = {
    'length': {
        'header': '',
        'tooltip': 'Unit-cell length of the selected structure in angstroms.',
        'url': 'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Icell_length_.html',
        'default': (3, 'ang')
    },
    'angle': {
        'header': '',
        'tooltip': 'Unit-cell angle of the selected structure in degrees.',
        'url': 'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Icell_angle_.html',
        'default': (90, 'deg')
    }
}


class Lattice(LoggedPathDict):
    """
    Container for a crystallographic unit cell
    """

    def __init__(self, length_a: Base, length_b: Base, length_c: Base,
                 angle_alpha: Base, angle_beta: Base, angle_gamma: Base):
        """
        Constructor for the crystallographic unit cell

        :param length_a: Unit cell length a
        :param length_b: Unit cell length b
        :param length_c:  Unit cell length c
        :param angle_alpha: Unit cell angle alpha
        :param angle_beta:  Unit cell angle beta
        :param angle_gamma:  Unit cell angle gamma
        """

        super().__init__(length_a=length_a, length_b=length_b, length_c=length_c,
                         angle_alpha=angle_alpha, angle_beta=angle_beta, angle_gamma=angle_gamma)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Lattice created: %s', self)

        self.setItemByPath(['length_a', 'header'], 'a (Å)')
        self.setItemByPath(['length_a', 'tooltip'], LATTICE_DETAILS['length']['tooltip'])
        self.setItemByPath(['length_a', 'url'], LATTICE_DETAILS['length']['url'])

        self.setItemByPath(['length_b', 'header'], 'b (Å)')
        self.setItemByPath(['length_b', 'tooltip'], LATTICE_DETAILS['length']['tooltip'])
        self.setItemByPath(['length_b', 'url'], LATTICE_DETAILS['length']['url'])

        self.setItemByPath(['length_c', 'header'], 'c (Å)')
        self.setItemByPath(['length_c', 'tooltip'], LATTICE_DETAILS['length']['tooltip'])
        self.setItemByPath(['length_c', 'url'], LATTICE_DETAILS['length']['url'])

        self.setItemByPath(['angle_alpha', 'header'], 'alpha (°)')
        self.setItemByPath(['angle_alpha', 'tooltip'], LATTICE_DETAILS['angle']['tooltip'])
        self.setItemByPath(['angle_alpha', 'url'], LATTICE_DETAILS['angle']['url'])

        self.setItemByPath(['angle_beta', 'header'], 'beta (°)')
        self.setItemByPath(['angle_beta', 'tooltip'], LATTICE_DETAILS['angle']['tooltip'])
        self.setItemByPath(['angle_beta', 'url'], LATTICE_DETAILS['angle']['url'])

        self.setItemByPath(['angle_gamma', 'header'], 'gamma (°)')
        self.setItemByPath(['angle_gamma', 'tooltip'], LATTICE_DETAILS['angle']['tooltip'])
        self.setItemByPath(['angle_gamma', 'url'], LATTICE_DETAILS['angle']['url'])

    @classmethod
    def default(cls) -> 'Lattice':
        """
        Default constructor for a crystallographic unit cell

        :return: Default crystolographic unit cell container
        """
        length_a = Base(*LATTICE_DETAILS['length']['default'])
        length_b = Base(*LATTICE_DETAILS['length']['default'])
        length_c = Base(*LATTICE_DETAILS['length']['default'])
        angle_alpha = Base(*LATTICE_DETAILS['angle']['default'])
        angle_beta = Base(*LATTICE_DETAILS['angle']['default'])
        angle_gamma = Base(*LATTICE_DETAILS['angle']['default'])
        return cls(length_a, length_b, length_c, angle_alpha, angle_beta, angle_gamma)

    @classmethod
    def fromPars(cls, length_a: float, length_b: float, length_c: float,
                 angle_alpha: float, angle_beta: float, angle_gamma: float) -> 'Lattice':
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
        length_a = Base(length_a, LATTICE_DETAILS['length']['default'][1])
        length_b = Base(length_b, LATTICE_DETAILS['length']['default'][1])
        length_c = Base(length_c, LATTICE_DETAILS['length']['default'][1])
        angle_alpha = Base(angle_alpha, LATTICE_DETAILS['angle']['default'][1])
        angle_beta = Base(angle_beta, LATTICE_DETAILS['angle']['default'][1])
        angle_gamma = Base(angle_gamma, LATTICE_DETAILS['angle']['default'][1])

        return cls(length_a=length_a, length_b=length_b, length_c=length_c,
                   angle_alpha=angle_alpha, angle_beta=angle_beta, angle_gamma=angle_gamma)

    def __repr__(self) -> str:
        return 'Lattice: (a:{}, b:{}, c:{}, alpha:{}, beta:{}, gamma:{}) '.format(self['length_a'], self['length_b'],
                                                                               self['length_c'],
                                                                               self['angle_alpha'], self['angle_beta'],
                                                                               self['angle_gamma'])

    @property
    def length_a(self):
        return self['length_a'].value

    @length_a.setter
    def length_a(self, value):
        self['length_a'].value = value

    @property
    def length_b(self):
        return self['length_b'].value

    @length_b.setter
    def length_b(self, value):
        self['length_b'].value = value

    @property
    def length_c(self):
        return self['length_c'].value

    @length_c.setter
    def length_c(self, value):
        self['length_c'].value = value

    @property
    def a(self):
        return self['length_a'].value

    @a.setter
    def a(self, value):
        self['length_a'].value = value

    @property
    def b(self):
        return self['length_b'].value

    @b.setter
    def b(self, value):
        self['length_b'].value = value

    @property
    def c(self):
        return self['length_c'].value

    @c.setter
    def c(self, value):
        self['length_c'].value = value

    @property
    def angle_alpha(self):
        return self['angle_alpha'].value

    @angle_alpha.setter
    def angle_alpha(self, value):
        self['angle_alpha'].value = value

    @property
    def angle_beta(self):
        return self['angle_beta'].value

    @angle_beta.setter
    def angle_beta(self, value):
        self['angle_beta'].value = value

    @property
    def angle_gamma(self):
        return self['angle_gamma'].value

    @angle_gamma.setter
    def angle_gamma(self, value):
        self['angle_gamma'].value = value

    @property
    def alpha(self):
        return self['angle_alpha'].value

    @alpha.setter
    def alpha(self, value):
        self['angle_alpha'].value = value

    @property
    def beta(self):
        return self['angle_beta'].value

    @beta.setter
    def beta(self, value):
        self['angle_beta'].value = value

    @property
    def gamma(self):
        return self['angle_gamma'].value

    @gamma.setter
    def gamma(self, value):
        self['angle_gamma'].value = value
