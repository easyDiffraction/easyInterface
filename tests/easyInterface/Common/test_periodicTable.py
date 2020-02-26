#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 26/02/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import json
import os
import pytest

from easyInterface.Common.periodicTable import Element, Specie

with open(os.path.join('tests', 'Data', 'elements.json'), 'r') as file_reader:
    elements = json.loads(file_reader.read())


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    argnames = ['element', 'raw_data']
    for scenario in metafunc.cls.scenarios:
        idlist.append(scenario[0])
        argvalues.append([scenario[0], scenario[1]])
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestElementWithScenarios:
    scenarios = elements

    @pytest.fixture
    def element_class(self, element):
        return Element(element)

    def test_Element_from_z(self, element, element_class, raw_data):
        this_element = Element.from_Z(raw_data['Atomic no'])
        assert this_element == element_class
        assert this_element.Z == raw_data['Atomic no']
        assert element == this_element.symbol

    def test_str(self, element, element_class, raw_data):
        assert str(element_class) == element

    def test_symbol(self, element, element_class, raw_data):
        assert element == element_class.symbol

    def test_z(self, element, element_class, raw_data):
        assert element_class.Z == raw_data['Atomic no']

    def test_atomic_radius(self, element, element_class, raw_data):
        unit = 'ang'
        radius = raw_data['Atomic radius']
        if radius == 'no data':
            radius = None
            with pytest.raises(AttributeError):
                assert str(element_class.atomic_radius.unit) == unit
        else:
            assert str(element_class.atomic_radius.unit) == unit
        assert element_class.atomic_radius == radius

    def test_atomic_mass(self, element, element_class, raw_data):
        unit = 'amu'
        mass = raw_data['Atomic mass']
        assert pytest.approx(element_class.atomic_mass, mass)
        assert str(element_class.atomic_mass.unit) == unit

    def test_number(self, element, element_class, raw_data):
        assert element_class.number == raw_data['Atomic no']

    def test_max_oxidation_state(self, element, element_class, raw_data):
        assert element_class.max_oxidation_state == max(raw_data.get('Oxidation states', [0]))

    def test_min_oxidation_state(self, element, element_class, raw_data):
        assert element_class.min_oxidation_state == min(raw_data.get('Oxidation states', [0]))

    def test_oxidation_states(self, element, element_class, raw_data):
        assert element_class.oxidation_states == tuple(raw_data.get('Oxidation states', list()))

    def test_common_oxidation_states(self, element, element_class, raw_data):
        assert element_class.common_oxidation_states == tuple(raw_data.get('Common oxidation states', list()))

    def test_full_electronic_structure(self, element, element_class, raw_data):
        assert isinstance(element_class.full_electronic_structure, list)

    def test_group(self, element, element_class, raw_data):
        group = element_class.group
        assert isinstance(group, int)
        assert group == raw_data['Group']

    # def test_valence(self, element, element_class, raw_data):
    #     assert False
    #
    # def test_scattering_lengths(self, element, element_class, raw_data):
    #     assert False

    def test_block(self, element, element_class, raw_data):
        block = element_class.block
        assert isinstance(block, str)
        assert block == raw_data['Block']

    def test_is_noble_gas(self, element, element_class, raw_data):
        NG = element_class.is_noble_gas
        assert isinstance(NG, bool)
        assert NG == raw_data['isNG']

    def test_is_transition_metal(self, element, element_class, raw_data):
        TM = element_class.is_transition_metal
        assert isinstance(TM, bool)
        assert TM == raw_data['isTM']

    def test_is_post_transition_metal(self, element, element_class, raw_data):
        TM = element_class.is_post_transition_metal
        assert isinstance(TM, bool)
        assert TM == raw_data['ispTM']

    def test_is_rare_earth_metal(self, element, element_class, raw_data):
        RE = element_class.is_rare_earth_metal
        assert isinstance(RE, bool)
        assert RE == raw_data['isRE']

    def test_is_metal(self, element, element_class, raw_data):
        M = element_class.is_metal
        assert isinstance(M, bool)
        assert M == raw_data['isM']

    def test_is_metalloid(self, element, element_class, raw_data):
        M = element_class.is_post_transition_metal
        assert isinstance(M, bool)
        assert M == raw_data['isMo']

    def test_is_alkali(self, element, element_class, raw_data):
        M = element_class.is_alkali
        assert isinstance(M, bool)
        assert M == raw_data['isAL']

    def test_is_alkaline(self, element, element_class, raw_data):
        M = element_class.is_alkaline
        assert isinstance(M, bool)
        assert M == raw_data['isAK']

    def test_is_halogen(self, element, element_class, raw_data):
        M = element_class.is_halogen
        assert isinstance(M, bool)
        assert M == raw_data['isH']

    def test_is_chalcogen(self, element, element_class, raw_data):
        M = element_class.is_chalcogen
        assert isinstance(M, bool)
        assert M == raw_data['isC']

    def test_is_lanthanoid(self, element, element_class, raw_data):
        M = element_class.is_lanthanoid
        assert isinstance(M, bool)
        assert M == raw_data['isLa']

    def test_is_actinoid(self, element, element_class, raw_data):
        M = element_class.is_actinoid
        assert isinstance(M, bool)
        assert M == raw_data['isAC']

    def test_is_quadrupolar(self, element, element_class, raw_data):
        M = element_class.is_quadrupolar
        assert isinstance(M, bool)
        assert M == raw_data['isQP']

    def test_nmr_quadrupole_moment(self, element, element_class, raw_data):
        moment = element_class.nmr_quadrupole_moment
        assert moment == raw_data['nmr_moment']
