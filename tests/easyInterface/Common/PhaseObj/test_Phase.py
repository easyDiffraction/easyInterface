from easyInterface.Common.PhaseObj.Phase import *
from tests.easyInterface.Common.Utils.Helpers import PathDictDerived


def genericTestPhase(phase_constructor, *args):
    expected = ['phasename', 'spacegroup', 'cell', 'atoms', 'sites']

    expected_type = [str, SpaceGroup, Cell, (Atom, dict, Atoms), dict]
    PathDictDerived(phase_constructor, expected, expected_type, *args)

    return phase_constructor(*args)


def test_phase_default():
    name = 'boo'
    phase = genericTestPhase(Phase.default, name)

    site = phase['sites']
    keys = ['fract_x', 'fract_y', 'fract_z', 'scat_length_neutron']
    for key in site.keys():
        assert key in keys
        assert isinstance(site[key], list)
        assert len(site[key]) == 0

    atoms = phase['atoms']
    assert isinstance(atoms, Atoms)
    assert len(atoms) == 0

    assert phase['phasename'] == name


def test_phase_from_pars():
    name = 'boo'
    sg = SpaceGroup.default()
    cell = Cell.default()

    phase = genericTestPhase(Phase.fromPars, name, sg, cell)

    site = phase['sites']
    keys = ['fract_x', 'fract_y', 'fract_z', 'scat_length_neutron']
    for key in site.keys():
        assert key in keys
        assert isinstance(site[key], list)
        assert len(site[key]) == 0

    atoms = phase['atoms']
    assert isinstance(atoms, Atoms)
    assert len(atoms) == 0

    assert phase['phasename'] == name
    assert phase['spacegroup'] == sg
    assert phase['cell'] == cell


def test_phases():
    phases = Phases([])
    assert len(phases) == 0
    phase = Phase.default('boo')
    phases[phase['phasename']] = phases
    assert len(phases) == 1
    phases = Phases([phase])
    assert len(phases) == 1
    assert phase['phasename'] in phases.keys()
    phases = Phases(phase)
    assert len(phases) == 1
    assert phase['phasename'] in phases.keys()


def test_phases_rename_phase():
    phase = Phase.default('boo')
    phases = Phases([phase])
    phases.renamePhase('boo', 'woo')
    assert 'woo' in phases.keys()
    assert phases['woo']['phasename'] == 'woo'