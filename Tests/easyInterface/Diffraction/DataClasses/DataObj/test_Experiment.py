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
    expected = ['name', 'ttheta', 'intensity']

    expected_type = [str, float, Base]
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
    expected = ['x', 'y_obs', 'sy_obs', 'y_obs_up', 'sy_obs_up', 'y_obs_down', 'sy_obs_down']
    expected_type = [*[list]*3, *[(list, type(None))]*4]
    
    PathDictDerived(MeasuredPattern.default, expected, expected_type)
    mp = MeasuredPattern.default()
    assert len(mp['x']) == 0
    assert len(mp['y_obs']) == 0
    assert len(mp['sy_obs']) == 0
    assert mp['y_obs_up'] is None
    assert mp['sy_obs_up'] is None
    assert mp['y_obs_down'] is None
    assert mp['sy_obs_down'] is None
    
    PathDictDerived(MeasuredPattern.default, expected, expected_type, True)
    mp = MeasuredPattern.default(True)
    assert len(mp['x']) == 0
    assert len(mp['y_obs']) == 0
    assert len(mp['sy_obs']) == 0
    assert len(mp['y_obs_up']) == 0
    assert len(mp['sy_obs_up']) == 0
    assert len(mp['y_obs_down']) == 0
    assert len(mp['sy_obs_down']) == 0
    
    PathDictDerived(MeasuredPattern.default, expected, expected_type, False)
    mp = MeasuredPattern.default(False)
    assert len(mp['x']) == 0
    assert len(mp['y_obs']) == 0
    assert len(mp['sy_obs']) == 0
    assert mp['y_obs_up'] is None
    assert mp['sy_obs_up'] is None
    assert mp['y_obs_down'] is None
    assert mp['sy_obs_down'] is None


def test_measured_pattern_is_polarised():
    mp = MeasuredPattern.default(True)
    assert mp.isPolarised
    mp = MeasuredPattern.default(False)
    assert not mp.isPolarised

    
def test_measured_pattern_y_obs_upper():
    x = list(range(0, 5))
    y = list(range(1, 6))
    err = [0.2]*len(x)
    mp = MeasuredPattern(x, y, err)
    
    assert mp.y_obs_upper == [yy + ee for yy, ee in zip(y, err)]


def test_measured_pattern_y_obs_lower():
    x = list(range(0, 5))
    y = list(range(1, 6))
    err = [0.2] * len(x)
    mp = MeasuredPattern(x, y, err)

    assert mp.y_obs_lower == [yy - ee for yy, ee in zip(y, err)]


def test_exp_phase_default():
    expected = ['name', 'scale']
    expected_type = [str, Base]
    name = 'boo'

    PathDictDerived(ExperimentPhase.default, expected, expected_type, name)
    ep = ExperimentPhase.default(name)
    assert ep['name'] == name
    assert ep.getItemByPath(['scale', 'header']) == SCALE_DETAILS['scale']['header']
    assert ep.getItemByPath(['scale', 'tooltip']) == SCALE_DETAILS['scale']['tooltip']
    assert ep.getItemByPath(['scale', 'url']) == SCALE_DETAILS['scale']['url']
    assert str(ep['scale']['store']['unit']) == SCALE_DETAILS['scale']['default'][1]
    assert ep['scale'].value == SCALE_DETAILS['scale']['default'][0]


def test_exp_phase_from_pars():
    expected = ['name', 'scale']
    expected_type = [str, Base]

    scale = 500.5
    name = 'boo'

    PathDictDerived(ExperimentPhase.fromPars, expected, expected_type, name, scale)
    ep = ExperimentPhase.fromPars(name, scale)
    assert ep['name'] == name
    assert ep.getItemByPath(['scale', 'header']) == SCALE_DETAILS['scale']['header']
    assert ep.getItemByPath(['scale', 'tooltip']) == SCALE_DETAILS['scale']['tooltip']
    assert ep.getItemByPath(['scale', 'url']) == SCALE_DETAILS['scale']['url']
    assert str(ep['scale']['store']['unit']) == SCALE_DETAILS['scale']['default'][1]
    assert ep['scale'].value == scale


def genericTestExperiment(exp_constructor, *args):
    expected = ['name', 'wavelength', 'offset', 'phase', 'background', 'resolution', 'measured_pattern']

    expected_type = [str, Base, Base, ExperimentPhases, Backgrounds, Resolution, MeasuredPattern]
    PathDictDerived(exp_constructor, expected, expected_type, *args)

    exp = exp_constructor(*args)

    assert exp.getItemByPath(['wavelength', 'header']) == EXPERIMENT_DETAILS['wavelength']['header']
    assert exp.getItemByPath(['offset', 'header']) == EXPERIMENT_DETAILS['offset']['header']

    assert exp.getItemByPath(['wavelength', 'tooltip']) == EXPERIMENT_DETAILS['wavelength']['tooltip']
    assert exp.getItemByPath(['offset', 'tooltip']) == EXPERIMENT_DETAILS['offset']['tooltip']

    assert exp.getItemByPath(['wavelength', 'url']) == EXPERIMENT_DETAILS['wavelength']['url']
    assert exp.getItemByPath(['offset', 'url']) == EXPERIMENT_DETAILS['offset']['url']

    return exp


def test_exp_default():
    name = 'boo'
    exp = genericTestExperiment(Experiment.default, name)

    assert exp['name'] == name
    assert str(exp['wavelength']['store']['unit']) == EXPERIMENT_DETAILS['wavelength']['default'][1]
    assert exp['wavelength'].value == EXPERIMENT_DETAILS['wavelength']['default'][0]
    assert str(exp['offset']['store']['unit']) == EXPERIMENT_DETAILS['offset']['default'][1]
    assert exp['offset'].value == EXPERIMENT_DETAILS['offset']['default'][0]


def test_exp_from_pars():
    name = 'boo'
    wavelength = 2.5
    offset = 0.01
    scale = 207.1
    background = Backgrounds({})
    resolution = Resolution.default()
    measured_pattern = MeasuredPattern.default()

    exp = genericTestExperiment(Experiment.fromPars, name, wavelength, offset, scale, background, resolution,
                                measured_pattern)

    assert exp['name'] == name
    assert str(exp['wavelength']['store']['unit']) == EXPERIMENT_DETAILS['wavelength']['default'][1]
    assert exp['wavelength'].value == wavelength
    assert str(exp['offset']['store']['unit']) == EXPERIMENT_DETAILS['offset']['default'][1]
    assert exp['offset'].value == offset

    assert exp['phase'][name]['scale'].value == scale
    assert len(exp['background']) == 0
    assert isinstance(exp['resolution'], Resolution)
    assert isinstance(measured_pattern, MeasuredPattern)


def test_exps():
    exps = Experiments([])
    assert len(exps) == 0
    exp = Experiment.default('boo')
    exps[exp['name']] = exps
    assert len(exps) == 1
    exps = Experiments([exp])
    assert len(exps) == 1
    assert exp['name'] in exps.keys()
    exps = Experiments(exp)
    assert len(exps) == 1
    assert exp['name'] in exps.keys()


def test_exps_get_names():

    exp_list = ['boo', 'woo', 'foo']
    exps_list = []
    for exp in exp_list:
        exps_list.append(Experiment.default(exp))
    exps = Experiments(exps_list)
    names = exps.getNames()
    assert names == exp_list


