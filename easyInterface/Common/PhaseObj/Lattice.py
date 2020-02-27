#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 26/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.2'

from typing import Tuple

import numpy as np

from easyInterface import logger as logging
from easyInterface.Utils.Typing import Vector3Like
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
    def matrix(self):
        angles_r = self.abg_rad
        cos_alpha, cos_beta, cos_gamma = np.cos(angles_r)
        sin_alpha, sin_beta, sin_gamma = np.sin(angles_r)

        val = (cos_alpha * cos_beta - cos_gamma) / (sin_alpha * sin_beta)
        gamma_star = np.arccos(val)

        vector_a = [self.a * sin_beta, 0.0, self.a * cos_beta]
        vector_b = [
            -self.b * sin_alpha * np.cos(gamma_star),
            self.b * sin_alpha * np.sin(gamma_star),
            self.b * cos_alpha,
        ]
        vector_c = [0.0, 0.0, self.c]
        return np.array([vector_a, vector_b, vector_c], dtype=np.float64)

    @property
    def length_a(self) -> float:
        return self['length_a'].value

    @length_a.setter
    def length_a(self, value: float):
        self['length_a'].value = value

    @property
    def length_b(self) -> float:
        return self['length_b'].value

    @length_b.setter
    def length_b(self, value: float):
        self['length_b'].value = value

    @property
    def length_c(self) -> float:
        return self['length_c'].value

    @length_c.setter
    def length_c(self, value: float):
        self['length_c'].value = value

    @property
    def a(self) -> float:
        return self['length_a'].value

    @a.setter
    def a(self, value: float):
        self['length_a'].value = value

    @property
    def b(self) -> float:
        return self['length_b'].value

    @b.setter
    def b(self, value: float):
        self['length_b'].value = value

    @property
    def c(self) -> float:
        return self['length_c'].value

    @c.setter
    def c(self, value: float):
        self['length_c'].value = value

    @property
    def abc(self) -> Tuple[float, float, float]:
        return self.a, self.b, self.c

    @property
    def angle_alpha(self) -> float:
        return self['angle_alpha'].value

    @angle_alpha.setter
    def angle_alpha(self, value: float):
        self['angle_alpha'].value = value

    @property
    def angle_beta(self) -> float:
        return self['angle_beta'].value

    @angle_beta.setter
    def angle_beta(self, value: float):
        self['angle_beta'].value = value

    @property
    def angle_gamma(self) -> float:
        return self['angle_gamma'].value

    @angle_gamma.setter
    def angle_gamma(self, value: float):
        self['angle_gamma'].value = value

    @property
    def alpha(self) -> float:
        return self['angle_alpha'].value

    @alpha.setter
    def alpha(self, value: float):
        self['angle_alpha'].value = value

    @property
    def beta(self) -> float:
        return self['angle_beta'].value

    @beta.setter
    def beta(self, value: float):
        self['angle_beta'].value = value

    @property
    def gamma(self) -> float:
        return self['angle_gamma'].value

    @gamma.setter
    def gamma(self, value: float):
        self['angle_gamma'].value = value

    @property
    def abg(self) -> Tuple[float, float, float]:
        return self.alpha, self.beta, self.gamma

    @property
    def abg_rad(self) -> Tuple[float, float, float]:
        return np.deg2rad(self.alpha), np.deg2rad(self.beta), np.deg2rad(self.gamma)

    @property
    def alpha_rad(self) -> float:
        """
        First lattice angle in radians
        """
        return self.abg_rad[0]

    @property
    def beta_rad(self) -> float:
        """
        Second lattice angle in radians
        """
        return self.abg_rad[1]

    @property
    def gamma_rad(self) -> float:
        """
        Third lattice angle in radians
        """
        return self.abg_rad[2]

    @property
    def astar(self) -> float:
        """
        First inverse lattice constant in inverse Angstrom
        """
        return self.b * self.c * np.sin(self.alpha_rad) / self.volume * 2 * np.pi

    @property
    def bstar(self) -> float:
        """
        Second inverse lattice constant in inverse Angstrom
        """
        return self.a * self.c * np.sin(self.beta_rad) / self.volume * 2 * np.pi

    @property
    def cstar(self) -> float:
        """
        Third inverse lattice constant in inverse Angstrom
        """
        return self.a * self.b * np.sin(self.gamma_rad) / self.volume * 2 * np.pi

    @property
    def alphastar_rad(self) -> float:
        """
        First inverse lattice angle in radians
        """
        return np.arccos((np.cos(self.beta_rad) * np.cos(self.gamma_rad) -
                          np.cos(self.alpha_rad)) /
                         (np.sin(self.beta_rad) * np.sin(self.gamma_rad)))

    @property
    def betastar_rad(self) -> float:
        """
        Second inverse lattice angle in radians
        """
        return np.arccos((np.cos(self.alpha_rad) *
                          np.cos(self.gamma_rad) -
                          np.cos(self.beta_rad)) /
                         (np.sin(self.alpha_rad) * np.sin(self.gamma_rad)))

    @property
    def gammastar_rad(self) -> float:
        """
        Third inverse lattice angle in radians
        """
        return np.arccos((np.cos(self.alpha_rad) * np.cos(self.beta_rad) -
                          np.cos(self.gamma_rad)) /
                         (np.sin(self.alpha_rad) * np.sin(self.beta_rad)))

    @property
    def alphastar(self) -> float:
        """
        First inverse lattice angle in degrees
        """
        return np.rad2deg(self.alphastar_rad)

    @property
    def betastar(self) -> float:
        """
        First inverse lattice angle in degrees
        """
        return np.rad2deg(self.betastar_rad)

    @property
    def gammastar(self) -> float:
        """
        First inverse lattice angle in degrees
        """
        return np.rad2deg(self.gammastar_rad)

    @property
    def reciprocal_abc(self) -> Vector3Like:
        """
        Reciprocal lattice constants in inverse Angstrom returned in list
        """
        return [self.astar, self.bstar, self.cstar]

    @property
    def reciprocal_abg(self) -> Vector3Like:
        """
        Reciprocal lattice angles in degrees returned in list
        """
        return [self.alphastar, self.betastar, self.gammastar]

    @property
    def reciprocal_abg_rad(self) -> Vector3Like:
        """
        Reciprocal lattice angles in radians returned in list
        """
        return [self.alphastar_rad, self.betastar_rad, self.gammastar_rad]

    @property
    def lattice_type(self) -> str:
        """
        Type of lattice determined by the provided lattice constants and angles
        """

        if len(np.unique(self.abc)) == 3 and len(np.unique(self.abg)) == 3:
            return 'triclinic'
        elif len(np.unique(self.abc)) == 3 and self.abg[1] != 90 and np.all(np.array(self.abg)[:3:2] == 90):
            return 'monoclinic'
        elif len(np.unique(self.abc)) == 3 and np.all(np.array(self.abg) == 90):
            return 'orthorhombic'
        elif len(np.unique(self.abc)) == 1 and len(np.unique(self.abg)) == 1 and np.all(
                        np.array(self.abg) < 120) and np.all(np.array(self.abg) != 90):
            return 'rhombohedral'
        elif len(np.unique(self.abc)) == 2 and self.abc[0] == self.abc[1] and np.all(np.array(self.abg) == 90):
            return 'tetragonal'
        elif len(np.unique(self.abc)) == 2 and self.abc[0] == self.abc[1] and np.all(np.array(self.abg)[0:2] == 90) and \
                        self.abg[2] == 120:
            return 'hexagonal'
        elif len(np.unique(self.abc)) == 1 and np.all(np.array(self.abg) == 90):
            return 'cubic'
        else:
            raise ValueError('Provided lattice constants and angles do not resolve to a valid Bravais lattice')

    @property
    def volume(self) -> float:
        u"""
        Volume of the unit cell in \u212B\ :sup:`3`
        """
        return np.sqrt(np.linalg.det(self.G))

    @property
    def reciprocal_volume(self) -> float:
        u"""
        Volume of the reciprocal unit cell in (\u212B\ :sup:`-1`\ )\ :sup:`3`
        """
        return np.sqrt(np.linalg.det(self.Gstar))

    @property
    def G(self) -> np.ndarray:
        """
        Metric tensor of the real space lattice
        """

        a, b, c = self.abc
        alpha, beta, gamma = self.abg_rad

        return np.array([[a ** 2, a * b * np.cos(gamma), a * c * np.cos(beta)],
                          [a * b * np.cos(gamma), b ** 2, b * c * np.cos(alpha)],
                          [a * c * np.cos(beta), b * c * np.cos(alpha), c ** 2]], dtype=float)

    @property
    def Gstar(self) -> np.ndarray:
        """
        Metric tensor of the reciprocal lattice
        """

        return np.linalg.inv(self.G) * 4 * np.pi ** 2

    @property
    def Bmatrix(self) -> np.ndarray:
        """
        Cartesian basis matrix in reciprocal units such that
        Bmatrix*Bmatrix.T = Gstar
        """

        return np.array([[self.astar, self.bstar * np.cos(self.gammastar_rad),  self.cstar * np.cos(self.betastar_rad)],
                          [0, self.bstar * np.sin(self.gammastar_rad), -self.cstar * np.sin(self.betastar_rad) * np.cos(self.alpha_rad)],
                          [0, 0, self.cstar * np.sin(self.betastar_rad) * np.sin(self.alphastar_rad)]], dtype=float)

    def get_d_spacing(self, hkl: Vector3Like) -> float:
        u"""
        Returns the d-spacing of a given reciprocal lattice vector.

        :param hkl: Reciprocal lattice vector in r.l.u.
        :return d: The d-spacing in \u212B
        """
        hkl = np.array(hkl)

        return float(1 / np.sqrt(np.dot(np.dot(hkl, self.Gstar / 4 / np.pi ** 2), hkl)))

    def get_angle_between_planes(self, v1: Vector3Like, v2: Vector3Like) -> float:
        """
        Returns the angle :math:`\phi` between two reciprocal lattice
        vectors (or planes as defined by the vectors normal to the plane).

        :param v1: First reciprocal lattice vector in units r.l.u.
        :param v2: Second reciprocal lattice vector in units r.l.u.

        :return phi: The angle between v1 and v2 in degrees
        """

        v1, v2 = np.array(v1), np.array(v2)

        return float(np.rad2deg(np.arccos(np.inner(np.inner(v1, self.Gstar), v2) /
                                          np.sqrt(np.inner(np.inner(v1, self.Gstar), v1)) /
                                          np.sqrt(np.inner(np.inner(v2, self.Gstar), v2)))))

    def get_two_theta(self, hkl: Vector3Like, wavelength: float) -> float:
        u"""Returns the detector angle 2\U0001D703 for a given reciprocal
        lattice vector and incident wavelength.

        :param hkl: Reciprocal lattice vector in r.l.u.
        :param wavelength: Wavelength of the incident beam in \u212B

        :return two_theta: The angle of the detector 2\U0001D703 in degrees
        """

        return 2 * np.rad2deg(np.arcsin(wavelength / 2 /
                                        self.get_d_spacing(hkl)))

    def get_q(self, hkl: Vector3Like) -> float:
        u"""Returns the magnitude of *Q* for a given reciprocal lattice
        vector in \u212B\ :sup:`-1`.

        :param hkl: Reciprocal lattice vector in r.l.u.

        :return q: The magnitude of the reciprocal lattice vector *Q* in \u212B\ :sup:`-1`
        """

        return 2 * np.pi / self.get_d_spacing(hkl)

    def dot(
            self, coords_a: Vector3Like, coords_b: Vector3Like, frac_coords: bool = False
    ) -> np.ndarray:
        """
        Compute the scalar product of vector(s).

        :param coords_a, coords_b: Array-like objects with the coordinates.
        :param frac_coords: Boolean stating whether the vector corresponds to fractional or cartesian coordinates.

        :return: Dot product
        """
        coords_a, coords_b = (
            np.reshape(coords_a, (-1, 3)),
            np.reshape(coords_b, (-1, 3)),
        )

        if len(coords_a) != len(coords_b):
            raise ValueError("")

        if np.iscomplexobj(coords_a) or np.iscomplexobj(coords_b):
            raise TypeError("Complex array!")

        if not frac_coords:
            cart_a, cart_b = coords_a, coords_b
        else:
            cart_a = np.reshape(
                [self.get_cartesian_coords(vec) for vec in coords_a], (-1, 3)
            )
            cart_b = np.reshape(
                [self.get_cartesian_coords(vec) for vec in coords_b], (-1, 3)
            )

        return np.array([dot(a, b) for a, b in zip(cart_a, cart_b)])

    def norm(self, coords: Vector3Like, frac_coords: bool = True) -> float:
        """
        Compute the norm of vector(s).
        Args:
            coords:
                Array-like object with the coordinates.
            frac_coords:
                Boolean stating whether the vector corresponds to fractional or
                cartesian coordinates.
        Returns:
            one-dimensional `numpy` array.
        """
        return np.sqrt(self.dot(coords, coords, frac_coords=frac_coords))