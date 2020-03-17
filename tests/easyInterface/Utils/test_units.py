# coding: utf-8
#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 14/3/2020


import collections

import pytest

from easyInterface.Utils.units import (Energy, Time, Length, unitized, Mass, Memory,
                                       EnergyArray, TimeArray, LengthArray, Unit,
                                       FloatWithUnit, ArrayWithUnit, UnitError)


def test_init():
    u1 = Unit((("m", 1), ("s", -1)))
    assert str(u1) == "m s^-1"
    u2 = Unit("kg m ^ 2 s ^ -2")
    assert str(u2) == "J"
    assert str(u1 * u2) == "J m s^-1"
    assert str(u2 / u1) == "J s m^-1"
    assert str(u1 / Unit("m")) == "Hz"
    assert str(u1 * Unit("s")) == "m"

    acc = u1 / Unit("s")
    newton = Unit("kg") * acc
    assert str(newton * Unit("m")) == "N m"


def test_energy():
    a = Energy(1.1, "eV")
    b = a.to("Ha")
    pytest.approx(b, 0.0404242579378)
    c = Energy(3.14, "J")
    pytest.approx(c.to("eV"), 1.9598338493806797e+19)
    pytest.raises(UnitError, Energy, 1, "m")

    d = Energy(1, "Ha")
    pytest.approx(a + d, 28.311386245987997)
    pytest.approx(a - d, -26.111386245987994)
    assert a + 1 == 2.1
    assert str(a / d) == "1.1 eV Ha^-1"


def test_time():
    a = Time(20, "h")
    pytest.approx(float(a.to("s")), 3600 * 20)
    # Test left and right multiplication.
    b = a * 3
    pytest.approx(float(b), 60.0)
    assert str(b.unit) == "h"
    assert float(3 * a) == 60.0
    a = Time(0.5, "d")
    pytest.approx(float(a.to("s")), 3600 * 24 * 0.5)


def test_length():
    x = Length(4.2, "ang")
    pytest.approx(x.to("cm"), 4.2e-08)
    assert x.to("pm") == 420
    assert str(x / 2) == "2.1 Å"
    y = x ** 3
    pytest.approx(y, 74.088)
    assert str(y.unit) == "Å^3"


def test_memory():
    mega = Memory(1, "Mb")
    assert mega.to("byte") == 1024 ** 2
    assert mega == Memory(1, "mb")

    same_mega = Memory.from_string("1Mb")
    assert same_mega.unit_type == "memory"

    other_mega = Memory.from_string("+1.0 mb")
    assert mega == other_mega


def test_unitized():
    @unitized("eV")
    def f():
        return [1, 2, 3]

    assert str(f()[0]) == "1.0 eV"
    assert isinstance(f(), list)

    @unitized("eV")
    def g():
        return 2, 3, 4

    assert str(g()[0]) == "2.0 eV"
    assert isinstance(g(), tuple)

    @unitized("pm")
    def h():
        d = collections.OrderedDict()
        for i in range(3):
            d[i] = i * 20
        return d

    assert str(h()[1]) == "20.0 pm"
    assert isinstance(h(), collections.OrderedDict)

    @unitized("kg")
    def i():
        return FloatWithUnit(5, "g")

    assert i() == FloatWithUnit(0.005, "kg")

    @unitized("kg")
    def j():
        return ArrayWithUnit([5, 10], "g")

    j_out = j()
    assert j_out.unit == Unit("kg")
    assert j_out[0] == 0.005
    assert j_out[1] == 0.01


def test_compound_operations():
    g = 10 * Length(1, "m") / (Time(1, "s") ** 2)
    e = Mass(1, "kg") * g * Length(1, "m")
    assert str(e) == "10.0 N m"

    form_e = FloatWithUnit(10, unit="kJ mol^-1").to("eV atom^-1")
    pytest.approx(float(form_e), 0.103642691905)
    assert str(form_e.unit) == "eV atom^-1"
    pytest.raises(UnitError, form_e.to, "m s^-1")
    a = FloatWithUnit(1.0, "Ha^3")
    b = a.to("J^3")
    pytest.approx(b, 8.28672661615e-53)
    assert str(b.unit) == "J^3"
    a = FloatWithUnit(1.0, "Ha bohr^-2")
    b = a.to("J m^-2")
    pytest.approx(b, 1556.8931028218924)
    assert str(b.unit) == "J m^-2"


def test_as_base_units():
    x = FloatWithUnit(5, "MPa")
    assert FloatWithUnit(5000000, "Pa") == x.as_base_units


def test_energyFWU():
    """
    Similar to FloatWithUnitTest.test_energy.
    Check whether EnergyArray and FloatWithUnit have same behavior.

    for obj in [Energy, EnergyArray]:
        a = obj(...)
        self.assert(...)

    """
    a = EnergyArray(1.1, "eV")
    b = a.to("Ha")
    pytest.approx(float(b), 0.0404242579378)
    c = EnergyArray(3.14, "J")
    pytest.approx(float(c.to("eV")), 1.9598338493806797e+19, 5)
    # pytest.raises(ValueError, Energy, 1, "m")

    d = EnergyArray(1, "Ha")
    pytest.approx(float(a + d), 28.311386245987997)
    pytest.approx(float(a - d), -26.111386245987994)
    assert float(a + 1) == 2.1


def test_timeFWU():
    """
    Similar to FloatWithUnitTest.test_time.
    Check whether EnergyArray and FloatWithUnit have same behavior.
    """
    # here there's a minor difference because we have a ndarray with
    # dtype=np.int.
    a = TimeArray(20, "h")
    pytest.approx(a.to("s"), 3600 * 20)
    # Test left and right multiplication.
    assert str(a * 3) == "60 h"
    assert str(3 * a) == "60 h"


def test_lengthFWU():
    """
    Similar to FloatWithUnitTest.test_time.
    Check whether EnergyArray and FloatWithUnit have same behavior.
    """
    x = LengthArray(4.2, "ang")
    pytest.approx(float(x.to("cm")), 4.2e-08)
    assert float(x.to("pm")) == 420
    assert str(x / 2) == "2.1 \u212B"


def test_array_algebra():
    ene_ha = EnergyArray([1, 2], "Ha")
    ene_ev = EnergyArray([1, 2], "eV")
    time_s = TimeArray([1, 2], "s")

    e1 = ene_ha.copy()
    e1 += 1
    e2 = ene_ha.copy()
    e2 -= 1
    e3 = ene_ha.copy()
    # e3 /= 2
    e4 = ene_ha.copy()
    e4 *= 2

    objects_with_unit = [
        ene_ha + ene_ev,
        ene_ha - ene_ev,
        3 * ene_ha,
        ene_ha * 3,
        ene_ha / 3,
        3 / ene_ha,
        ene_ha * time_s,
        ene_ha / ene_ev,
        ene_ha.copy(),
        ene_ha[0:1],
        e1,
        e2,
        e3,
        e4,
    ]

    for i, obj in enumerate(objects_with_unit):
        assert hasattr(obj, "unit")

    objects_without_unit = [
        # Here we could return a FloatWithUnit object but I prefer this
        # a bare scalar since FloatWithUnit extends float while we could
        # have an int.
        ene_ha[0],
    ]

    for obj in objects_without_unit:
        assert not hasattr(obj, "unit")

    with pytest.raises(UnitError):
        ene_ha + time_s


def test_factors():
    e = EnergyArray([27.21138386, 1], "eV").to("Ha")
    assert str(e).endswith("Ha")
    l = LengthArray([1.0], "ang").to("bohr")
    assert str(l).endswith(" bohr")
    v = ArrayWithUnit([1, 2, 3], "bohr^3").to("ang^3")
    assert str(v).endswith(' \u212B^3')
