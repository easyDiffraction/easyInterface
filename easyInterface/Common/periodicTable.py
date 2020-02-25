#  Licensed under the GNU General Public License v3.0
#  Copyright (c) of the author (github.com/wardsimon)
#  Created: 25/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from copy import deepcopy
from typing import Callable, List, Tuple, Union

import json
import re
import warnings
from pathlib import Path

import numpy as np
from easyInterface import logger, logging
from easyInterface.Utils.units import Mass, Length, FloatWithUnit, ComplexWithUnit, Unit, SUPPORTED_UNIT_NAMES

# Loads element data from json file
with open(str(Path(__file__).absolute().parent / "PT_WSL.json"), "r") as f:
    _pt_data = json.load(f)

_pt_row_sizes = (2, 8, 8, 18, 18, 32, 32)


class Element:

    def __init__(self, symbol: str):
        self._log = logger.getLogger(__class__.__module__)
        self._symbol = '{}'.format(symbol)
        try:
            data = _pt_data[self.symbol]
            self._data = self.__parse_element_data(data)
            for key in self._data.keys():
                this_key = '_' + key
                if self._data[key] is None:
                    continue
                setattr(self.__class__, this_key, property(self.__gitem(key)))

        except KeyError:
            self._log.error('Element {} is unknown.'.format(self.symbol))
            raise KeyError

        self.long_name = self._data["name"]

    @classmethod
    def from_Z(cls, z: int):
        """
        Get an element from an atomic number.

        Args:
            z (int): Atomic number

        Returns:
            Element with atomic number z.
        """
        for sym, data in _pt_data.items():
            if data["Atomic no"] == z:
                return cls(sym)
        raise ValueError("No element with this atomic number %s" % z)

    def __eq__(self, other):
        return isinstance(other, Element) and self.Z == other.Z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.Z

    def __repr__(self):
        return "Element " + self.symbol

    def __str__(self):
        return self.symbol

    def str(self):
        return self.__str__()

    def __deepcopy__(self, memo={}):
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

    @property
    def symbol(self):
        return self._symbol

    @property
    def Z(self) -> int:
        return int(self._atomic_no)

    @property
    def atomic_radius(self) -> float:
        """
        Returns: The atomic radius of the element in Ångstroms.
        """
        # Note that we have to do it like this due to He
        return getattr(self, '_atomic_radius', None)

    @property
    def atomic_mass(self) -> float:
        """
        Returns: The atomic mass of the element in amu.
        """
        return self._atomic_mass

    @property
    def number(self) -> float:
        """Alternative attribute for atomic number"""
        return self._atomic_no

    @property
    def max_oxidation_state(self) -> float:
        """Maximum oxidation state for element"""
        return max(getattr(self, '_oxidation_states', [0]))

    @property
    def min_oxidation_state(self) -> float:
        """Minimum oxidation state for element"""
        return min(getattr(self, '_oxidation_states', [0]))

    @property
    def oxidation_states(self) -> tuple:
        """Tuple of all known oxidation states"""
        return tuple(getattr(self, "_oxidation_states", list()))

    @property
    def common_oxidation_states(self) -> tuple:
        """Tuple of all known oxidation states"""
        return tuple(getattr(self, "_common_oxidation_states", list()))

    @property
    def full_electronic_structure(self) -> List[Tuple]:
        """
        Full electronic structure as tuple.
        E.g., The electronic structure for Fe is represented as:
        [(1, "s", 2), (2, "s", 2), (2, "p", 6), (3, "s", 2), (3, "p", 6),
        (3, "d", 6), (4, "s", 2)]
        """
        estr = self._electronic_structure

        def parse_orbital(orbstr):
            m = re.match(r"(\d+)([spdfg]+)<sup>(\d+)</sup>", orbstr)
            if m:
                return int(m.group(1)), m.group(2), int(m.group(3))
            return orbstr

        data = [parse_orbital(s) for s in estr.split(".")]
        if data[0][0] == "[":
            sym = data[0].replace("[", "").replace("]", "")
            data = Element(sym).full_electronic_structure + data[1:]
        return data

    @property
    def group(self):
        """
        Returns the periodic table group of the element.
        """
        z = self.Z
        if z == 1:
            return 1
        if z == 2:
            return 18
        if 3 <= z <= 18:
            if (z - 2) % 8 == 0:
                return 18
            if (z - 2) % 8 <= 2:
                return (z - 2) % 8
            return 10 + (z - 2) % 8

        if 19 <= z <= 54:
            if (z - 18) % 18 == 0:
                return 18
            return (z - 18) % 18

        if (z - 54) % 32 == 0:
            return 18
        if (z - 54) % 32 >= 18:
            return (z - 54) % 32 - 14
        return (z - 54) % 32

    @property
    def valence(self) -> tuple:
        """
        # From full electron config obtain valence subshell
        # angular moment (L) and number of valence e- (v_e)

        """
        # the number of valence of noble gas is 0
        if self.group == 18:
            return (np.nan, 0)

        L_symbols = 'SPDFGHIKLMNOQRTUVWXYZ'
        valence = []
        full_electron_config = self.full_electronic_structure
        for _, l_symbol, ne in full_electron_config[::-1]:
            l = L_symbols.lower().index(l_symbol)
            if ne < (2 * l + 1) * 2:
                valence.append((l, ne))
        if len(valence) > 1:
            raise ValueError("Ambiguous valence")

        return valence[0]

    @property
    def scattering_lengths(self) -> dict:
        return self._data['n_scattering_lengths']

    @property
    def block(self) -> str:
        """
        Return the block character "s,p,d,f"
        """
        if (self.is_actinoid or self.is_lanthanoid) and self.Z not in [71, 103]:
            return "f"
        if self.is_actinoid or self.is_lanthanoid:
            return "d"
        if self.group in [1, 2]:
            return "s"
        if self.group in range(13, 19):
            return "p"
        if self.group in range(3, 13):
            return "d"
        raise ValueError("unable to determine block")

    @property
    def is_noble_gas(self) -> bool:
        """
        True if element is noble gas.
        """
        return self.Z in (2, 10, 18, 36, 54, 86, 118)

    @property
    def is_transition_metal(self) -> bool:
        """
        True if element is a transition metal.
        """
        ns = list(range(21, 31))
        ns.extend(list(range(39, 49)))
        ns.append(57)
        ns.extend(list(range(72, 81)))
        ns.append(89)
        ns.extend(list(range(104, 113)))
        return self.Z in ns

    @property
    def is_post_transition_metal(self) -> bool:
        """
        True if element is a post-transition or poor metal.
        """
        return self.symbol in ("Al", "Ga", "In", "Tl", "Sn", "Pb", "Bi")

    @property
    def is_rare_earth_metal(self) -> bool:
        """
        True if element is a rare earth metal.
        """
        return self.is_lanthanoid or self.is_actinoid

    @property
    def is_metal(self) -> bool:
        """
        :return: True if is a metal.
        """
        return (self.is_alkali or self.is_alkaline or
                self.is_post_transition_metal or self.is_transition_metal or
                self.is_lanthanoid or self.is_actinoid)

    @property
    def is_metalloid(self) -> bool:
        """
        True if element is a metalloid.
        """
        return self.symbol in ("B", "Si", "Ge", "As", "Sb", "Te", "Po")

    @property
    def is_alkali(self) -> bool:
        """
        True if element is an alkali metal.
        """
        return self.Z in (3, 11, 19, 37, 55, 87)

    @property
    def is_alkaline(self) -> bool:
        """
        True if element is an alkaline earth metal (group II).
        """
        return self.Z in (4, 12, 20, 38, 56, 88)

    @property
    def is_halogen(self) -> bool:
        """
        True if element is a halogen.
        """
        return self.Z in (9, 17, 35, 53, 85)

    @property
    def is_chalcogen(self) -> bool:
        """
        True if element is a chalcogen.
        """
        return self.Z in (8, 16, 34, 52, 84)

    @property
    def is_lanthanoid(self) -> bool:
        """
        True if element is a lanthanoid.
        """
        return 56 < self.Z < 72

    @property
    def is_actinoid(self) -> bool:
        """
        True if element is a actinoid.
        """
        return 88 < self.Z < 104

    @property
    def is_quadrupolar(self) -> bool:
        """
        Checks if this element can be quadrupolar
        """
        return len(getattr(self, "_nmr_quadrupole_moment", {})) > 0

    @property
    def nmr_quadrupole_moment(self) -> dict:
        """
        Get a dictionary the nuclear electric quadrupole moment in units of
        e*millibarns for various isotopes
        """
        return {k: FloatWithUnit(v, "mbarn")
                for k, v in getattr(self, "_nmr_quadrupole_moment", {}).items()}

    @staticmethod
    def __parse_element_data(data: dict) -> dict:

        new_data = deepcopy(data)

        for item in data.keys():
            new_item = item.lower().replace(' ', '_')
            val = data.get(item, None)
            if str(val).startswith("no data"):
                val = None
            elif isinstance(val, dict):
                if new_item == 'n_scattering_lengths':
                    for isotope in val.keys():
                        for details in val[isotope].keys():
                            if val[isotope][details] is None:
                                del val[isotope][details]
                            if details[-1:] == 's':
                                val[isotope][details] = FloatWithUnit(val[isotope][details], 'barn')
                            elif details[-1:] == 'b':
                                if isinstance(val[isotope][details], list):
                                    val[isotope][details] = ComplexWithUnit(complex(val[isotope][details][0],val[isotope][details][1]), 'fm')
                                else:
                                    val[isotope][details] = FloatWithUnit(val[isotope][details], 'fm')
                            else:
                                if isinstance(val[isotope][details], str):
                                    val[isotope][details] = None
                                else:
                                    val[isotope][details] /= 100

            else:
                try:
                    if new_item == 'atomic_radius':
                        val = FloatWithUnit(val, 'ang')
                    elif new_item == 'atomic_mass':
                        val = FloatWithUnit(val, 'amu')
                    else:
                        val = float(val)
                except TypeError:
                    pass
                except ValueError:
                    nobracket = re.sub(r'\(.*\)', "", val)
                    toks = nobracket.replace("about", "").strip().split(" ", 1)
                    if len(toks) == 2:
                        try:
                            if "10<sup>" in toks[1]:
                                base_power = re.findall(r'([+-]?\d+)', toks[1])
                                factor = "e" + base_power[1]
                                if toks[0] in ["&gt;", "high"]:
                                    toks[0] = "1"  # return the border value
                                toks[0] += factor
                                if new_item == "electrical_resistivity":
                                    unit = "ohm m"
                                elif new_item == "coefficient_of_linear_thermal_expansion":
                                    unit = "K^-1"
                                else:
                                    unit = toks[1]
                                val = FloatWithUnit(toks[0], unit)
                            else:
                                unit = toks[1].replace("<sup>", "^").replace(
                                    "</sup>", "").replace("&Omega;",
                                                          "ohm")
                                units = Unit(unit)
                                if set(units.keys()).issubset(
                                        SUPPORTED_UNIT_NAMES):
                                    val = FloatWithUnit(toks[0], unit)
                        except ValueError:
                            # Ignore error. val will just remain a string.
                            pass
            new_data[new_item] = val
            del new_data[item]
        return new_data

    @staticmethod
    def __gitem(key: str) -> Callable:
        return lambda obj: obj._data[key]

    @staticmethod
    def __sitem(key):
        return lambda obj, value: obj._data.__setitem__(key, value)


class Specie(Element):

    __supported_properties = ("spin",)

    def __init__(self, symbol: str, oxidation_state: int = 0, **kwargs):
        symbol_oxi_regex = re.compile("([a-zA-Z]+)([0-9+-]+)")
        oxi_regex = re.compile("([0-9]+)([+-]+)")
        symbol_oxi_match = symbol_oxi_regex.match(symbol)
        v_set = True
        if symbol_oxi_match is None:
            oxi = oxidation_state
            v_set = False
        else:
            symbol = symbol_oxi_match.group(1)
            state = symbol_oxi_match.group(2)
            if state[0] == '-' or state[0] == '+':
                oxi = 1
                state = state[0]
            else:
                oxi_match = oxi_regex.match(state)
                oxi = int(oxi_match.group(1))
                state = oxi_match.group(2)
            if state == '-':
                oxi = -1*oxi
        super().__init__(symbol)
        if oxi not in self.oxidation_states and v_set:
            Exception('Oxidation state {} is unknown for element {}. Available states are:\n{}', oxi, symbol, self.oxidation_states)
        self.oxi_state = oxi
        for key in kwargs.keys():
            if key not in Specie.__supported_properties:
                raise ValueError("{} is not a supported property".format(key))
            else:
                self._data['_' + key] = kwargs[key]
                setattr(self.__class__, key, property(self.__gitem(key), self.__sitem(key)))

    def __repr__(self) -> str:
        return "Specie " + self.__str__()

    def __str__(self) -> str:
        output = self.symbol
        if self.oxi_state is not None:
            if self.oxi_state > 0:
                output += formula_double_format(self.oxi_state) + "+"
            elif self.oxi_state < 0:
                output += formula_double_format(-self.oxi_state) + "-"
        for prop in Specie.__supported_properties:
            if hasattr(self, prop):
                output += ",%s=%s" % (prop, getattr(self, prop))
        return output

    def get_nmr_quadrupole_moment(self, isotope: Union[str, type(None)] = None) -> float:
        """
        Gets the nuclear electric quadrupole moment in units of
        e*millibarns

        Args:
            isotope (str): the isotope to get the quadrupole moment for
                default is None, which gets the lowest mass isotope
        """

        quad_mom = super().nmr_quadrupole_moment

        if not quad_mom:
            return 0.0

        if isotope is None:
            isotopes = list(quad_mom.keys())
            isotopes.sort(key=lambda x: int(x.split("-")[1]), reverse=False)
            return quad_mom.get(isotopes[0], 0.0)

        if isotope not in quad_mom:
            raise ValueError("No quadrupole moment for isotope {}".format(isotope))
        return quad_mom.get(isotope, 0.0)

    def get_shannon_radius(self, cn: str, spin: str = "",
                           radius_type: str = "ionic"):
        """
        Get the local environment specific ionic radius for species.

        Args:
            cn (str): Coordination using roman letters. Supported values are
                I-IX, as well as IIIPY, IVPY and IVSQ.
            spin (str): Some species have different radii for different
                spins. You can get specific values using "High Spin" or
                "Low Spin". Leave it as "" if not available. If only one spin
                data is available, it is returned and this spin parameter is
                ignored.
            radius_type (str): Either "crystal" or "ionic" (default).

        Returns:
            Shannon radius for specie in the specified environment.
        """
        radii = self._shannon_radii
        radii = radii[str(int(self.oxi_state))][cn]  # type: ignore
        if len(radii) == 1:  # type: ignore
            k, data = list(radii.items())[0]  # type: ignore
            if k != spin:
                warnings.warn(
                    "Specified spin state of %s not consistent with database "
                    "spin of %s. Only one spin data available, and "
                    "that value is returned." % (spin, k)
                )
        else:
            data = radii[spin]
        return data["%s_radius" % radius_type]

    def get_crystal_field_spin(self, coordination: str = "oct",
                               spin_config: str = "high") -> int:
        """
        Calculate the crystal field spin based on coordination and spin
        configuration. Only works for transition metal species.

        Args:
            coordination (str): Only oct and tet are supported at the moment.
            spin_config (str): Supported keywords are "high" or "low".

        Returns:
            Crystal field spin in Bohr magneton.

        Raises:
            AttributeError if species is not a valid transition metal or has
            an invalid oxidation state.
            ValueError if invalid coordination or spin_config.
        """

        if coordination not in ("oct", "tet") or spin_config not in ("high", "low"):
            raise ValueError("Invalid coordination or spin config.")
        elec = self.full_electronic_structure
        if len(elec) < 4 or elec[-1][1] != "s" or elec[-2][1] != "d":
            raise AttributeError(
                "Invalid element {} for crystal field calculation.".format(self.symbol))
        nelectrons = elec[-1][2] + elec[-2][2] - self.oxi_state
        if nelectrons < 0 or nelectrons > 10:
            raise AttributeError(
                "Invalid oxidation state {} for element {}".format(self.oxi_state, self.symbol))
        if spin_config == "high":
            if nelectrons <= 5:
                return nelectrons
            return 10 - nelectrons
        if spin_config == "low":
            if coordination == "oct":
                if nelectrons <= 3:
                    return nelectrons
                if nelectrons <= 6:
                    return 6 - nelectrons
                if nelectrons <= 8:
                    return nelectrons - 6
                return 10 - nelectrons
            if coordination == "tet":
                if nelectrons <= 2:
                    return nelectrons
                if nelectrons <= 4:
                    return 4 - nelectrons
                if nelectrons <= 7:
                    return nelectrons - 4
                return 10 - nelectrons
        raise RuntimeError()


def formula_double_format(afloat, ignore_ones=True, tol=1e-8):
    """
    This function is used to make pretty formulas by formatting the amounts.
    Instead of Li1.0 Fe1.0 P1.0 O4.0, you get LiFePO4.
    Args:
        afloat (float): a float
        ignore_ones (bool): if true, floats of 1 are ignored.
        tol (float): Tolerance to round to nearest int. i.e. 2.0000000001 -> 2
    Returns:
        A string representation of the float for formulas.
    """
    if ignore_ones and afloat == 1:
        return ""
    elif abs(afloat - int(afloat)) < tol:
        return str(int(afloat))
    else:
        return str(round(afloat, 8))