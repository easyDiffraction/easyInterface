from easyInterface.Diffraction.DataClasses.DataObj.Experiment import *
from Tests.easyInterface.Diffraction.DataClasses.Utils.Helpers import PathDictDerived


def genericTestResolution(res_constructor, *args):
    expected = ['u', 'v', 'w', 'x', 'y']

    expected_type = [Base, Base, Base, Base, Base]
    PathDictDerived(res_constructor, expected, expected_type, *args)

    res = res_constructor(*args)

    assert res.getItemByPath(['u', 'header']) == RESOLUTION_DETAILS['UVWXY']['header']
    assert res.getItemByPath(['v', 'header']) == RESOLUTION_DETAILS['UVWXY']['header']
    assert res.getItemByPath(['w', 'header']) == RESOLUTION_DETAILS['UVWXY']['header']
    assert res.getItemByPath(['x', 'header']) == RESOLUTION_DETAILS['UVWXY']['header']
    assert res.getItemByPath(['y', 'header']) == RESOLUTION_DETAILS['UVWXY']['header']

    assert res.getItemByPath(['u', 'tooltip']) == RESOLUTION_DETAILS['UVWXY']['tooltip']
    assert res.getItemByPath(['v', 'tooltip']) == RESOLUTION_DETAILS['UVWXY']['tooltip']
    assert res.getItemByPath(['w', 'tooltip']) == RESOLUTION_DETAILS['UVWXY']['tooltip']
    assert res.getItemByPath(['x', 'tooltip']) == RESOLUTION_DETAILS['UVWXY']['tooltip']
    assert res.getItemByPath(['y', 'tooltip']) == RESOLUTION_DETAILS['UVWXY']['tooltip']

    assert res.getItemByPath(['u', 'url']) == RESOLUTION_DETAILS['UVWXY']['url']
    assert res.getItemByPath(['v', 'url']) == RESOLUTION_DETAILS['UVWXY']['url']
    assert res.getItemByPath(['w', 'url']) == RESOLUTION_DETAILS['UVWXY']['url']
    assert res.getItemByPath(['x', 'url']) == RESOLUTION_DETAILS['UVWXY']['url']
    assert res.getItemByPath(['y', 'url']) == RESOLUTION_DETAILS['UVWXY']['url']

    return res


def test_resolution_default():
    res = genericTestResolution(Resolution.default)

    assert str(res['u']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['u'].value == RESOLUTION_DETAILS['UVWXY']['default'][0]

    assert str(res['v']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['v'].value == RESOLUTION_DETAILS['UVWXY']['default'][0]

    assert str(res['w']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['w'].value == RESOLUTION_DETAILS['UVWXY']['default'][0]

    assert str(res['x']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['x'].value == RESOLUTION_DETAILS['UVWXY']['default'][0]

    assert str(res['y']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['y'].value == RESOLUTION_DETAILS['UVWXY']['default'][0]


def test_resolution_from_pars():
    val = 2

    res = genericTestResolution(Resolution.fromPars, val, val, val, val, val)

    assert str(res['u']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['u'].value == val

    assert str(res['v']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['v'].value == val

    assert str(res['w']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['w'].value == val

    assert str(res['x']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['x'].value == val

    assert str(res['y']['store']['unit']) == RESOLUTION_DETAILS['UVWXY']['default'][1]
    assert res['y'].value == val


def genericTestBackground(bg_constructor, *args):
    expected = ['ttheta', 'intensity']

    expected_type = [float, Base]
    PathDictDerived(bg_constructor, expected, expected_type, *args)

    bg = bg_constructor(*args)

    assert bg.getItemByPath(['intensity', 'header']) == INTENSITY_DETAILS['intensity']['header']
    assert bg.getItemByPath(['intensity', 'tooltip']) == INTENSITY_DETAILS['intensity']['tooltip']
    assert bg.getItemByPath(['intensity', 'url']) == INTENSITY_DETAILS['intensity']['url']

    return bg


def test_background_default():
    bg = genericTestBackground(Background.default)

    assert bg['ttheta'] == 0.0
    assert str(bg['intensity']['store']['unit']) == INTENSITY_DETAILS['intensity']['default'][1]
    assert bg['intensity'].value == INTENSITY_DETAILS['intensity']['default'][0]


def test_background_from_pars():

    ttheta = 32.1
    intensity = 100.0

    bg = genericTestBackground(Background.fromPars, ttheta, intensity)

    assert bg['ttheta'] == ttheta
    assert str(bg['intensity']['store']['unit']) == INTENSITY_DETAILS['intensity']['default'][1]
    assert bg['intensity'].value == intensity


def test_backgrounds():
    bgs = Backgrounds([])
    assert len(bgs) == 0
    bg = Background.default()
    bgs[str(bg['ttheta'])] = bgs
    assert len(bgs) == 1
    bgs = Backgrounds([bg])
    assert len(bgs) == 1
    assert str(bg['ttheta']) in bgs.keys()
    bgs = Backgrounds(bg)
    assert len(bgs) == 1
    assert str(bg['ttheta']) in bgs.keys()


def test_measured_pattern_default():
    assert False


def test_measured_pattern_is_polarised():
    assert False


def test_measured_pattern_y_obs_upper():
    assert False


def test_measured_pattern_y_obs_lower():
    assert False


def test_exp_phase_default():
    assert False


def test_exp_phase_from_pars():
    assert False


def test_exp_default():
    assert False


def test_exp_from_pars():
    assert False


def test_exps_get_names():
    assert False
