#  Licensed under the GNU General Public License v3.0
#  Copyright (c) of the author (github.com/wardsimon)
#  Created: 1/3/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.2'

import pytest

from easyInterface.Common.PhaseObj.Lattice import *
from tests.easyInterface.Common.Utils.Helpers import PathDictDerived

example_params = [('cubic', ((4, 'ang'), (4, 'ang'), (4, 'ang'), (90, 'deg'), (90, 'deg'), (90, 'deg'))),
                  ('triclinic', ((5, 'ang'), (4, 'ang'), (6, 'ang'), (95, 'deg'), (90, 'deg'), (89, 'deg'))),
                  ('monoclinic', ((6, 'ang'), (4, 'ang'), (5, 'ang'), (90, 'deg'), (99, 'deg'), (90, 'deg'))),
                  ('orthorhombic', ((6, 'ang'), (4, 'ang'), (5, 'ang'), (90, 'deg'), (90, 'deg'), (90, 'deg'))),
                  ('rhombohedral', ((6, 'ang'), (6, 'ang'), (6, 'ang'), (100, 'deg'), (100, 'deg'), (100, 'deg'))),
                  ('tetragonal', ((6, 'ang'), (6, 'ang'), (4, 'ang'), (90, 'deg'), (90, 'deg'), (90, 'deg'))),
                  ('hexagonal', ((4, 'ang'), (4, 'ang'), (5, 'ang'), (90, 'deg'), (90, 'deg'), (120, 'deg')))
                  ]

generator_pars = [(Lattice.cubic, [(5, 'ang')], 'cubic'),
                  (Lattice.tetragonal, [(5, 'ang'), (4, 'ang')], 'tetragonal'),
                  (Lattice.orthorhombic, [(5, 'ang'), (4, 'ang'), (6, 'ang')], 'orthorhombic'),
                  (Lattice.monoclinic, [(5, 'ang'), (4, 'ang'), (6, 'ang'), (105, 'deg')], 'monoclinic'),
                  (Lattice.hexagonal, [(5, 'ang'), (4, 'ang')], 'hexagonal'),
                  (Lattice.rhombohedral, [(4, 'ang'), (105, 'deg')], 'rhombohedral')]

hkl_pars = [[1, 1.2, 1.3],
            [1.2, 0.4, 0.6],
            [0.7, 1.8, 1]
            ]

wavelength_pars = [1, 0.8, 0.3]


def genericTestCell(cell_constructor, *args):
    expected = ['length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma']

    expected_type = [Parameter, Parameter, Parameter, Parameter, Parameter, Parameter]
    PathDictDerived(cell_constructor, expected, expected_type, *args)

    cell = cell_constructor(*args)

    assert cell.getItemByPath(['length_a']).header == 'a (Å)'
    assert cell.getItemByPath(['length_b']).header == 'b (Å)'
    assert cell.getItemByPath(['length_c']).header == 'c (Å)'
    assert cell.getItemByPath(['angle_alpha']).header == 'alpha (°)'
    assert cell.getItemByPath(['angle_beta']).header == 'beta (°)'
    assert cell.getItemByPath(['angle_gamma']).header == 'gamma (°)'

    assert cell.getItemByPath(['length_a']).tooltip == LENGTH_DEFAULTS['tooltip']
    assert cell.getItemByPath(['length_b']).tooltip == LENGTH_DEFAULTS['tooltip']
    assert cell.getItemByPath(['length_c']).tooltip == LENGTH_DEFAULTS['tooltip']
    assert cell.getItemByPath(['angle_alpha']).tooltip == ANGLE_DEFAULTS['tooltip']
    assert cell.getItemByPath(['angle_beta']).tooltip == ANGLE_DEFAULTS['tooltip']
    assert cell.getItemByPath(['angle_gamma']).tooltip == ANGLE_DEFAULTS['tooltip']

    assert cell.getItemByPath(['length_a']).url == LENGTH_DEFAULTS['url']
    assert cell.getItemByPath(['length_b']).url == LENGTH_DEFAULTS['url']
    assert cell.getItemByPath(['length_c']).url == LENGTH_DEFAULTS['url']
    assert cell.getItemByPath(['angle_alpha']).url == ANGLE_DEFAULTS['url']
    assert cell.getItemByPath(['angle_beta']).url == ANGLE_DEFAULTS['url']
    assert cell.getItemByPath(['angle_gamma']).url == ANGLE_DEFAULTS['url']

    return cell


def test_cell_default():
    cell = genericTestCell(Lattice.default)

    assert str(cell['length_a'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_a'].value == LENGTH_DEFAULTS['default'][0]

    assert str(cell['length_b'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_b'].value == LENGTH_DEFAULTS['default'][0]

    assert str(cell['length_c'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_c'].value == LENGTH_DEFAULTS['default'][0]

    assert str(cell['angle_alpha'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_alpha'].value == ANGLE_DEFAULTS['default'][0]

    assert str(cell['angle_beta'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_beta'].value == ANGLE_DEFAULTS['default'][0]

    assert str(cell['angle_gamma'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_gamma'].value == ANGLE_DEFAULTS['default'][0]


def test_cell_from_pars():
    length = 5
    angle = 60

    cell = genericTestCell(Lattice.fromPars, length, length, length, angle, angle, angle)

    assert str(cell['length_a'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_a'].value == length

    assert str(cell['length_b'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_b'].value == length

    assert str(cell['length_c'].value.unit) == LENGTH_DEFAULTS['default'][1]
    assert cell['length_c'].value == length

    assert str(cell['angle_alpha'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_alpha'].value == angle

    assert str(cell['angle_beta'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_beta'].value == angle

    assert str(cell['angle_gamma'].value.unit) == ANGLE_DEFAULTS['default'][1]
    assert cell['angle_gamma'].value == angle


class BaseGenerator:
    def __init__(self, input_vars):
        self.system = input_vars[0]
        self.expected_values = [par[0] for par in input_vars[1]]
        self.expected_units = [par[1] for par in input_vars[1]]
        self.lattice = Lattice.fromPars(*self.expected_values)
        self.HKL = None


class BaseEvaluator:
    def __init__(self, input_vars):
        self.system = input_vars[2]
        self.lattice = input_vars[0](*[par[0] for par in input_vars[1]])
        self.expected_values = [self.lattice['length_a'].value, self.lattice['length_b'].value,
                                self.lattice['length_c'].value, self.lattice['angle_alpha'].value,
                                self.lattice['angle_beta'].value, self.lattice['angle_gamma'].value]
        self.expected_units = [str(val) for val in [self.lattice['length_a'].unit, self.lattice['length_b'].unit,
                                                    self.lattice['length_c'].unit, self.lattice['angle_alpha'].unit,
                                                    self.lattice['angle_beta'].unit, self.lattice['angle_gamma'].unit]]
        self.HKL = None


@pytest.fixture(params=[*example_params, *generator_pars])
def param_loop(request):
    if isinstance(request.param[0], str):
        return BaseGenerator(request.param)
    else:
        return BaseEvaluator(request.param)


@pytest.fixture(params=hkl_pars)
def hkl_loop(request):
    return request.param


@pytest.fixture(params=wavelength_pars)
def wavelength_loop(request):
    return request.param


class TestClassFunctions:

    def test_length_a(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.length_a.value == expected_values[0]
        assert str(lattice.length_a.unit) == expected_units[0]

    def test_length_a_set(self, param_loop):
        lattice = param_loop.lattice

        value = 5.0
        with pytest.raises(AttributeError):
            lattice.length_a = value

    def test_length_a_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice['length_a'] = value
        assert lattice['length_a'].value == value
        assert str(lattice['length_a'].unit) == expected_units[0]

    def test_length_b(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.length_b.value == expected_values[1]
        assert str(lattice.length_b.unit) == expected_units[1]

    def test_length_b_set(self, param_loop):
        lattice = param_loop.lattice

        value = 5.0
        with pytest.raises(AttributeError):
            lattice.length_b = value

    def test_length_b_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice['length_b'] = value
        assert lattice['length_b'].value == value
        assert str(lattice['length_b'].unit) == expected_units[1]

    def test_length_c(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.length_c.value == expected_values[2]
        assert str(lattice.length_c.unit) == expected_units[2]

    def test_length_c_set(self, param_loop):
        lattice = param_loop.lattice

        value = 5.0
        with pytest.raises(AttributeError):
            lattice.length_c = value

    def test_length_c_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice['length_c'] = value
        assert lattice['length_c'].value == value
        assert str(lattice['length_c'].unit) == expected_units[2]

    def test_a(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.a == expected_values[0]
        assert str(lattice.a.unit) == expected_units[0]

    def test_a_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice.a = value
        assert lattice.a == value
        assert str(lattice.a.unit) == expected_units[0]

    def test_b(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.b == expected_values[1]
        assert str(lattice.b.unit) == expected_units[1]

    def test_b_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice.b = value
        assert lattice.b == value
        assert str(lattice.b.unit) == expected_units[1]

    def test_c(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.c == expected_values[2]
        assert str(lattice.c.unit) == expected_units[2]

    def test_c_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 5.0
        lattice.c = value
        assert lattice.c == value
        assert str(lattice.c.unit) == expected_units[2]

    def test_abc(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert lattice.abc == (expected_values[0],
                               expected_values[1],
                               expected_values[2])

    def test_angle_alpha(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.angle_alpha.value == expected_values[3]
        assert str(lattice.angle_alpha.unit) == expected_units[3]

    def test_angle_alpha_set(self, param_loop):
        lattice = param_loop.lattice

        value = 99.0
        with pytest.raises(AttributeError):
            lattice.angle_alpha = value

    def test_angle_alpha_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice['angle_alpha'] = value
        assert lattice['angle_alpha'].value == value
        assert str(lattice['angle_alpha'].value.unit) == expected_units[3]

    def test_angle_beta(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.angle_beta.value == expected_values[4]
        assert str(lattice.angle_beta.unit) == expected_units[4]

    def test_angle_beta_set(self, param_loop):
        lattice = param_loop.lattice

        value = 99.0
        with pytest.raises(AttributeError):
            lattice.angle_beta = value

    def test_angle_beta_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice['angle_beta'] = value
        assert lattice['angle_beta'].value == value
        assert str(lattice['angle_beta'].value.unit) == expected_units[4]

    def test_angle_gamma(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.angle_gamma.value == expected_values[5]
        assert str(lattice.angle_gamma.unit) == expected_units[5]

    def test_angle_gamma_set(self, param_loop):
        lattice = param_loop.lattice

        value = 99.0
        with pytest.raises(AttributeError):
            lattice.angle_gamma = value

    def test_angle_gamma_set_dict(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice['angle_gamma'] = value
        assert lattice['angle_gamma'].value == value
        assert str(lattice['angle_gamma'].value.unit) == expected_units[5]

    def test_alpha(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.alpha == expected_values[3]
        assert str(lattice.alpha.unit) == expected_units[3]

    def test_alpha_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice.alpha = value
        assert lattice.alpha == value
        assert str(lattice.alpha.unit) == expected_units[3]

    def test_beta(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.beta == expected_values[4]
        assert str(lattice.beta.unit) == expected_units[4]

    def test_beta_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice.beta = value
        assert lattice.beta == value
        assert str(lattice.beta.unit) == expected_units[4]

    def test_gamma(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert lattice.gamma == expected_values[5]
        assert str(lattice.gamma.unit) == expected_units[5]

    def test_gamma_set(self, param_loop):
        lattice = param_loop.lattice
        expected_units = param_loop.expected_units

        value = 99.0
        lattice.gamma = value
        assert lattice.gamma == value
        assert str(lattice.gamma.unit) == expected_units[5]

    def test_abg(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert lattice.abg == (expected_values[3],
                               expected_values[4],
                               expected_values[5])

    def test_abg_rad(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert np.all(lattice.abg_rad == np.deg2rad([expected_values[3],
                                                     expected_values[4],
                                                     expected_values[5]]))

    def test_alpha_rad(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert lattice.alpha_rad == np.deg2rad(expected_values[3])

    def test_beta_rad(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert lattice.beta_rad == np.deg2rad(expected_values[4])

    def test_gamma_rad(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values

        assert lattice.gamma_rad == np.deg2rad(expected_values[5])

    def test_astar(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = lambda b_in, c_in, alpha_in, vol_in: \
            b_in * c_in * np.sin(alpha_in) / vol_in * 2 * np.pi

        b = lattice.b
        c = lattice.c
        alpha = lattice.alpha_rad
        vol = lattice.volume

        assert lattice.astar == value(b, c, alpha, vol)

        # b = expected_values[1]
        # c = expected_values[2]
        # alpha = np.deg2rad(expected_values[3])
        # vol = lattice.volume

    def test_bstar(self, param_loop):
        lattice = param_loop.lattice

        a = lattice.a
        c = lattice.c
        beta = lattice.beta_rad
        vol = lattice.volume

        value = a * c * np.sin(beta) / vol * 2 * np.pi

        assert lattice.bstar == value

    def test_cstar(self, param_loop):
        lattice = param_loop.lattice

        a = lattice.a
        b = lattice.b
        gamma = lattice.gamma_rad
        vol = lattice.volume

        value = a * b * np.sin(gamma) / vol * 2 * np.pi

        assert lattice.cstar == value

    def test_alphastar_rad(self, param_loop):
        lattice = param_loop.lattice
        value = np.arccos((np.cos(lattice.beta_rad) * np.cos(lattice.gamma_rad) -
                           np.cos(lattice.alpha_rad)) /
                          (np.sin(lattice.beta_rad) * np.sin(lattice.gamma_rad)))

        assert value == lattice.alphastar_rad

    def test_betastar_rad(self, param_loop):
        lattice = param_loop.lattice
        value = np.arccos((np.cos(lattice.alpha_rad) *
                           np.cos(lattice.gamma_rad) -
                           np.cos(lattice.beta_rad)) /
                          (np.sin(lattice.alpha_rad) * np.sin(lattice.gamma_rad)))

        assert value == lattice.betastar_rad

    def test_gammastar_rad(self, param_loop):
        lattice = param_loop.lattice

        value = np.arccos((np.cos(lattice.alpha_rad) * np.cos(lattice.beta_rad) -
                           np.cos(lattice.gamma_rad)) /
                          (np.sin(lattice.alpha_rad) * np.sin(lattice.beta_rad)))

        assert value == lattice.gammastar_rad

    def test_alphastar(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = np.rad2deg(np.arccos((np.cos(lattice.beta_rad) * np.cos(lattice.gamma_rad) -
                                      np.cos(lattice.alpha_rad)) /
                                     (np.sin(lattice.beta_rad) * np.sin(lattice.gamma_rad))))

        assert value == lattice.alphastar

    def test_betastar(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = np.rad2deg(np.arccos((np.cos(lattice.alpha_rad) *
                                      np.cos(lattice.gamma_rad) -
                                      np.cos(lattice.beta_rad)) /
                                     (np.sin(lattice.alpha_rad) * np.sin(lattice.gamma_rad))))

        assert value == lattice.betastar

    def test_gammastar(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = np.rad2deg(np.arccos((np.cos(lattice.alpha_rad) * np.cos(lattice.beta_rad) -
                                      np.cos(lattice.gamma_rad)) /
                                     (np.sin(lattice.alpha_rad) * np.sin(lattice.beta_rad))))

        assert value == lattice.gammastar

    def test_reciprocal_abc(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert [lattice.astar, lattice.bstar, lattice.cstar] == lattice.reciprocal_abc

    def test_reciprocal_abg(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert [lattice.alphastar, lattice.betastar, lattice.gammastar] == \
               lattice.reciprocal_abg

    def test_reciprocal_abg_rad(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert [lattice.alphastar_rad, lattice.betastar_rad, lattice.gammastar_rad] == \
               lattice.reciprocal_abg_rad

    def test_lattice_type(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert param_loop.system == lattice.lattice_type

    def make_G(self, lattice):
        a = lattice.a
        b = lattice.b
        c = lattice.c
        alpha = lattice.alpha_rad
        beta = lattice.beta_rad
        gamma = lattice.gamma_rad

        value = np.array([[a ** 2, a * b * np.cos(gamma), a * c * np.cos(beta)],
                          [a * b * np.cos(gamma), b ** 2, b * c * np.cos(alpha)],
                          [a * c * np.cos(beta), b * c * np.cos(alpha), c ** 2]], dtype=float)
        return value

    def test_get_g(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        assert np.all(self.make_G(lattice) == lattice.get_G())

    def test_get_gstar(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        G = self.make_G(lattice)
        value = np.linalg.inv(G) * 4 * np.pi ** 2

        assert np.all(value == lattice.get_Gstar())

    def test_volume(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        G = self.make_G(lattice)
        value = np.sqrt(np.linalg.det(G))

        assert value == lattice.volume

    def test_reciprocal_volume(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        Gstar = lattice.get_Gstar()
        value = np.sqrt(np.linalg.det(Gstar))
        assert value == lattice.reciprocal_volume

    def test_get_bmatrix(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = np.array([[lattice.astar, lattice.bstar * np.cos(lattice.gammastar_rad),
                           lattice.cstar * np.cos(lattice.betastar_rad)],
                          [0, lattice.bstar * np.sin(lattice.gammastar_rad),
                           -lattice.cstar * np.sin(lattice.betastar_rad) * np.cos(lattice.alpha_rad)],
                          [0, 0, lattice.cstar * np.sin(lattice.betastar_rad) * np.sin(lattice.alphastar_rad)]],
                         dtype=float)

        assert np.all(value == lattice.get_Bmatrix())

    def test_matrix(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        angles_r = lattice.abg_rad
        cos_alpha, cos_beta, cos_gamma = np.cos(angles_r)
        sin_alpha, sin_beta, sin_gamma = np.sin(angles_r)

        val = (cos_alpha * cos_beta - cos_gamma) / (sin_alpha * sin_beta)
        gamma_star = np.arccos(val)

        vector_a = [lattice.a * sin_beta, 0.0, lattice.a * cos_beta]
        vector_b = [
            -lattice.b * sin_alpha * np.cos(gamma_star),
            lattice.b * sin_alpha * np.sin(gamma_star),
            lattice.b * cos_alpha,
        ]
        vector_c = [0.0, 0.0, lattice.c]
        assert np.all(np.array([vector_a, vector_b, vector_c], dtype=np.float64) == lattice.matrix)


class TestHKLFunctions:

    def test_get_d_spacing(self, param_loop, hkl_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units
        hkl = np.array(hkl_loop)
        d = float(1 / np.sqrt(np.dot(np.dot(hkl, lattice.get_Gstar() / 4 / np.pi ** 2), hkl)))
        assert lattice.get_d_spacing(hkl_loop) == d

    def test_get_two_theta(self, param_loop, hkl_loop, wavelength_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = 2 * np.rad2deg(np.arcsin(wavelength_loop / 2 /
                                         lattice.get_d_spacing(hkl_loop)))

        assert value == lattice.get_two_theta(hkl_loop, wavelength_loop)

    def test_get_q(self, param_loop, hkl_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        value = 2 * np.pi / lattice.get_d_spacing(hkl_loop)
        assert value == lattice.get_q(hkl_loop)


class TestCoOrdinateSystems:
    def test_get_cartesian_coords(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_co_ords = np.array(hkl_loop)
        abc = np.array(lattice.abc)
        cart_co_ords = fract_co_ords * abc

        assert np.all(cart_co_ords == lattice.get_cartesian_coords(hkl_loop))

    def test_get_cartesian_coordsMod(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_co_ords = np.array(hkl_loop)
        abc = np.array(lattice.abc)
        cart_co_ords = fract_co_ords * abc
        cart_co_ords = np.mod(cart_co_ords, abc)

        assert np.all(cart_co_ords == lattice.get_cartesian_coords(hkl_loop, mod=True))

    def test_get_cartesian_coordsMulti(self, param_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_co_ords = np.array(hkl_pars)
        abc = np.array(lattice.abc)
        cart_co_ords = fract_co_ords * abc

        assert np.all(cart_co_ords == lattice.get_cartesian_coords(hkl_pars))

    def test_get_cartesian_coordsModMulti(self, param_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_co_ords = np.array(hkl_pars)
        abc = np.array(lattice.abc)
        cart_co_ords = fract_co_ords * abc
        cart_co_ords = np.mod(cart_co_ords, abc)

        assert np.all(cart_co_ords == lattice.get_cartesian_coords(hkl_pars, mod=True))

    def test_get_fractional_coords(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        abc = np.array(hkl_loop)*np.array(lattice.abc)
        fract_co_ords = np.array(hkl_loop) / np.array(lattice.abc)

        assert np.all(fract_co_ords == lattice.get_fractional_coords(hkl_loop))

    def test_get_fractional_coordsMod(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        abc = np.array(hkl_loop)*np.array(lattice.abc)
        fract_co_ords = np.array(hkl_loop) / np.array(lattice.abc)
        fract_co_ords = np.mod(fract_co_ords, 1.0)

        assert np.all(fract_co_ords == lattice.get_fractional_coords(hkl_loop, mod=True))

    def test_get_fractional_coordsMulti(self, param_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        cart_co_ords = np.reshape(hkl_pars, (-1, 3))
        abc = np.array(cart_co_ords)*np.array(lattice.abc)
        fract_co_ords = cart_co_ords / np.array(lattice.abc)

        assert np.all(fract_co_ords == lattice.get_fractional_coords(hkl_pars))

    def test_get_fractional_coordsModMulti(self, param_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        cart_co_ords = np.reshape(hkl_pars, (-1, 3))
        abc = np.array(cart_co_ords)*np.array(lattice.abc)
        fract_co_ords = cart_co_ords / np.array(lattice.abc)
        fract_co_ords = np.mod(fract_co_ords, 1.0)

        assert np.all(fract_co_ords == lattice.get_fractional_coords(hkl_pars, mod=True))


class TestVectorMath:

    def test_dot_cart(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        cart_a = np.array(hkl_loop)*np.array(lattice.abc)
        hkl_loop.reverse()
        cart_b = np.array(hkl_loop)*np.array(lattice.abc)

        cart_a = np.reshape(cart_a, (-1, 3))
        cart_b = np.reshape(cart_b, (-1, 3))

        value = np.array([np.dot(a, b) for a, b in zip(cart_a, cart_b)])

        assert np.all(value == lattice.dot(cart_a, cart_b))

    def test_dot_frac(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_a = np.array(hkl_loop)
        hkl_loop.reverse()
        fract_b = np.array(hkl_loop)

        cart_a = lattice.get_cartesian_coords(fract_a)
        cart_b = lattice.get_cartesian_coords(fract_b)

        value = np.array([np.dot(a, b) for a, b in zip(cart_a, cart_b)])

        assert np.all(value == lattice.dot(fract_a, fract_b, frac_coords=True))

    def test_norm_frac(self, param_loop, hkl_loop):

        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        cart_a = np.array(hkl_loop)*np.array(lattice.abc)

        value = np.sqrt(lattice.dot(cart_a, cart_a))

        assert value == lattice.norm(hkl_loop)

    def test_norm_cart(self, param_loop, hkl_loop):
        lattice = param_loop.lattice
        expected_values = param_loop.expected_values
        expected_units = param_loop.expected_units

        fract_a = np.array(hkl_loop)
        cart_a = lattice.get_cartesian_coords(fract_a)

        value = np.sqrt(lattice.dot(cart_a, cart_a))

        assert value == lattice.norm(hkl_loop, frac_coords=True)
