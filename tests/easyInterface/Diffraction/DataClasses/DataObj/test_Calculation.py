from easyInterface.Diffraction.DataClasses.DataObj.Calculation import *
from tests.easyInterface.Diffraction.DataClasses.Utils.Helpers import PathDictDerived


def PathDictTest(path_dic, expected, expected_type):
    assert isinstance(path_dic, LoggedPathDict)
    keys = path_dic.keys()
    for index, key in enumerate(expected):
        assert key in keys
        assert isinstance(path_dic[key], expected_type[index])


def test_limits():
    # Empty Test
    expected = ['main', 'difference']
    expected_type = [LoggedPathDict, LoggedPathDict]

    PathDictDerived(Limits, expected, expected_type)
    lim = Limits()
    expected = ['x_min', 'x_max', 'y_min', 'y_max']
    expected_type = [float] * 4
    PathDictTest(lim['main'], expected, expected_type)
    expected = ['y_min', 'y_max']
    expected_type = [float] * 2
    PathDictTest(lim['difference'], expected, expected_type)
    main = lim['main']
    assert main['x_min'] == 0.0
    assert main['x_max'] == 0.0
    assert main['y_min'] == -np.Inf
    assert main['y_max'] == np.Inf
    difference = lim['difference']
    assert difference['y_min'] == -np.Inf
    assert difference['y_max'] == np.Inf

    # Data Test
    expected = ['main', 'difference']
    expected_type = [LoggedPathDict, LoggedPathDict]

    x = [float(x) for x in range(10)]
    y_obs_lower = [x_ - 0.1 for x_ in x]
    y_obs_upper = [x_ + 0.1 for x_ in x]
    y_diff_upper = [x_ + 0.25 for x_ in x]
    y_diff_lower = [x_ - 0.25 for x_ in x]
    x_calc = x
    y_calc = [x_ * 2 for x_ in x]

    PathDictDerived(Limits, expected, expected_type, y_obs_lower, y_obs_upper, y_diff_upper,
                    y_diff_lower, x_calc, y_calc)
    lim = Limits(y_obs_lower, y_obs_upper, y_diff_upper, y_diff_lower, x_calc, y_calc)
    expected = ['x_min', 'x_max', 'y_min', 'y_max']
    expected_type = [float] * 4
    PathDictTest(lim['main'], expected, expected_type)
    expected = ['y_min', 'y_max']
    expected_type = [float] * 2
    PathDictTest(lim['difference'], expected, expected_type)
    main = lim['main']
    assert main['x_min'] == 0.0
    assert main['x_max'] == 9.0
    assert main['y_min'] == -0.1
    assert main['y_max'] == 18.0
    difference = lim['difference']
    assert difference['y_min'] == -0.25
    assert difference['y_max'] == 9.25


def test_crystal_bragg_peaks():
    expected = ['name', 'h', 'k', 'l']
    expected_type = [str, *[list] * 4]

    name = 'boo'
    h = list(range(0, 100))
    k = list(range(0, 100))
    l = list(range(0, 100))
    ttheta = list(range(5, 105))
    bpc = CrystalBraggPeaks(name, h, k, l, ttheta)

    PathDictTest(bpc, expected, expected_type)
    assert bpc['name'] == name
    assert bpc['h'] == h
    assert bpc['k'] == k
    assert bpc['l'] == l
    assert bpc['ttheta'] == ttheta


def test_bragg_peaks():

    name = 'boo'
    h = list(range(0, 100))
    k = list(range(0, 100))
    l = list(range(0, 100))
    ttheta = list(range(5, 105))
    bpc = CrystalBraggPeaks(name, h, k, l, ttheta)

    bps = BraggPeaks([])
    assert len(bps) == 0
    bps[str(bpc['name'])] = bps
    assert len(bps) == 1
    bps = BraggPeaks([bpc])
    assert len(bps) == 1
    assert str(bpc['name']) in bps.keys()
    bps = BraggPeaks(bpc)
    assert len(bps) == 1
    assert str(bpc['name']) in bps.keys()


def test_calculated_pattern():
    x = list(range(10))
    y_calc = list(range(10, 20))
    y_diff_lower = [x_ - 0.1 for x_ in y_calc]
    y_diff_upper = [x_ + 0.1 for x_ in y_calc]
    expected = ['x', 'y_calc', 'y_diff_lower', 'y_diff_upper']
    expected_type = [list]*4
    cp = CalculatedPattern(x, y_calc, y_diff_lower, y_diff_upper)
    PathDictTest(cp, expected, expected_type)
    assert cp['x'] == x
    assert cp['y_calc'] == y_calc
    assert cp['y_diff_lower'] == y_diff_lower
    assert cp['y_diff_upper'] == y_diff_upper


def genericTestCalculation(cp_constructor, *args):
    expected = ['name', 'bragg_peaks', 'calculated_pattern', 'limits']
    expected_type = [str, BraggPeaks, CalculatedPattern, Limits]
    PathDictDerived(cp_constructor, expected, expected_type, *args)
    return cp_constructor(*args)


def test_calculation_default():
    name = 'boo'
    calc = genericTestCalculation(Calculation.default, name)
    assert calc['name'] == name
    assert len(calc['bragg_peaks']) == 0
    assert len(calc['calculated_pattern']['x']) == 1
    assert calc['calculated_pattern']['x'] == [0]
    main = calc['limits']['main']
    assert main['x_min'] == 0.0
    assert main['x_max'] == 0.0
    assert main['y_min'] == -np.Inf
    assert main['y_max'] == np.Inf
    difference = calc['limits']['difference']
    assert difference['y_min'] == -np.Inf
    assert difference['y_max'] == np.Inf


def test_calculation_from_pars():
    name = 'boo'
    h = list(range(0, 100))
    k = list(range(0, 100))
    l = list(range(0, 100))
    ttheta = list(range(5, 105))
    bragg_crystals = CrystalBraggPeaks(name, h, k, l, ttheta)
    x = [float(x) for x in range(10)]
    y_obs_lower = [x_ - 0.1 for x_ in x]
    y_obs_upper = [x_ + 0.1 for x_ in x]
    y_diff_upper = [x_ + 0.25 for x_ in x]
    y_diff_lower = [x_ - 0.25 for x_ in x]
    tth = x
    y_calc = [x_ * 2 for x_ in x]
    calc = genericTestCalculation(Calculation.fromPars, name, bragg_crystals, y_obs_lower,
                                  y_obs_upper, tth, y_calc, y_diff_lower, y_diff_upper)


def test_calculations():
    calcs = Calculations([])
    assert len(calcs) == 0
    name = 'boo'
    calc = Calculation.default(name)
    calcs[name] = calc
    assert len(calcs) == 1
    calcs = Calculations([calc])
    assert len(calcs) == 1
    assert name in calcs.keys()
    calcs = Calculations(calc)
    assert len(calcs) == 1
    assert name in calcs.keys()
