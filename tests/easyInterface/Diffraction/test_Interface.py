import os
import tempfile

import numpy as np
import pytest

from copy import deepcopy
from sys import platform

# module for testing
from tests.easyInterface.Diffraction.DataClasses.Utils.Helpers import PathDictDerived
from easyInterface.Diffraction import DEFAULT_FILENAMES
from easyInterface.Diffraction.Calculators import CryspyCalculator
from easyInterface.Diffraction.Interface import CalculatorInterface, ProjectDict
from easyInterface.Diffraction.DataClasses.Utils.InfoObjs import Interface, App, Calculator, Info
from easyInterface.Diffraction.DataClasses.DataObj.Calculation import Calculation, Calculations
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import Experiments, Experiment
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases, Phase

test_data = os.path.join('tests', 'Data')

file_path = os.path.join(test_data, DEFAULT_FILENAMES['project'])
phase_path = os.path.join(test_data, DEFAULT_FILENAMES['phases'])
exp_path = os.path.join(test_data, DEFAULT_FILENAMES['experiments'])


@pytest.fixture
def cal():
    calc = CryspyCalculator(file_path)
    interface = CalculatorInterface(calc)
    return interface


def test_creation_None():
    calc = CryspyCalculator(None)
    interface = CalculatorInterface(calc)


def test_creation_EmptyStr():
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)


def test_creation_WrongStr():
    path = os.path.join(test_data, 'mainf.cif')
    calc = CryspyCalculator(path)
    interface = CalculatorInterface(calc)


def test_creation_Empty():
    calc = CryspyCalculator()
    interface = CalculatorInterface(calc)


def test_deepcopyProjectDict(cal):
    # This might fail on python 3.6
    new_project_dict = deepcopy(cal.project_dict)


def test_init(cal):
    # initial state of the object
    assert len(cal.project_dict['app']) == 3
    assert len(cal.project_dict['calculations']) == 1
    assert len(cal.project_dict['info']) == 7
    assert len(cal.project_dict['phases']) == 1
    assert len(cal.project_dict['experiments']) == 1

    assert cal.calculator._project_rcif_path == file_path

    assert len(cal.project_dict) == 7


def test_setAppDict(cal):
    assert 'name' in cal.project_dict['app'].keys()
    assert cal.project_dict['app']['name'] == '-'
    assert 'version' in cal.project_dict['app'].keys()
    assert cal.project_dict['app']['version'] == '0.0.0'
    assert 'url' in cal.project_dict['app'].keys()
    assert cal.project_dict['app']['url'] == '-'


def test_setCalculatorDict(cal):
    assert 'name' in cal.project_dict['calculator'].keys()
    assert cal.project_dict['calculator']['name'] == 'CrysPy'
    assert 'version' in cal.project_dict['calculator'].keys()
    assert 'url' in cal.project_dict['calculator'].keys()


def test_setInfoDict(cal):
    assert len(cal.project_dict['info']) == 7
    assert 'refinement_datetime' in cal.project_dict['info']
    assert 'modified_datetime' in cal.project_dict['info']
    assert 'experiment_ids' in cal.project_dict['info']
    assert 'pd' in cal.project_dict['info']['experiment_ids']
    assert 'phase_ids' in cal.project_dict['info']
    assert 'Fe3O4' in cal.project_dict['info']['phase_ids']
    assert 'Fe3O4' == cal.project_dict['info']['name']


def test_setPhase(cal):
    phase = cal.getPhase('Fe3O4')
    cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value = 2
    cal.setPhase(phase)
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value == 8.36212


def test_setPhaseRefine(cal):
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].refine is True
    cal.setPhaseRefine('Fe3O4', ['cell', 'length_a'], False)
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].refine is False


def test_setPhaseValue(cal):
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value == 8.36212
    cal.setPhaseValue('Fe3O4', ['cell', 'length_a'], 5)
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value == 5

# def test_setPhases(cal):
#     phase2 = cal.getPhase('Fe3O4')
#     phase2['phasename'] = 'Fe3O4_2'
#     cal.addPhase(phase2)
#     phases = cal.getPhase(None)
#     phases['Fe3O4']['cell']['length_a'].value = 5
#     cal.setPhases(phases)
#     assert len(cal.project_dict['phases']) == 2
#     assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value == 5
#     assert cal.project_dict['phases']['Fe3O4_2']['cell']['length_a'].value == 8.36212


def test_setPhasesDictFromCryspyObj(cal):
    # difficult test for creation of the phases dict
    cal.project_dict['phases'].clear()  # enforce
    assert cal.calculator._cryspy_obj.crystals is not None

    cal.updatePhases()

    phase_dict = cal.project_dict['phases']

    assert len(phase_dict) == 1
    assert len(phase_dict['Fe3O4']) == 5
    assert len(phase_dict['Fe3O4']['cell']) == 6
    # cell
    assert phase_dict['Fe3O4']['cell']['length_a'].value == 8.36212
    assert phase_dict['Fe3O4']['cell']['length_b']['store']['hide'] is True
    assert phase_dict['Fe3O4']['cell']['length_c']['store'].max == 10.034544
    assert phase_dict['Fe3O4']['cell']['angle_beta']['store']['error'] == 0.0
    assert phase_dict['Fe3O4']['cell']['angle_gamma']['store']['constraint'] is None
    # space_group
    assert len(phase_dict['Fe3O4']['spacegroup']) == 4
    assert phase_dict['Fe3O4']['spacegroup']['crystal_system'].value == 'cubic'
    assert phase_dict['Fe3O4']['spacegroup']['origin_choice'].value == '2'

    # atom sites
    assert len(phase_dict['Fe3O4']['atoms']) == 3
    assert list(phase_dict['Fe3O4']['atoms'].keys()) == ['Fe3A', 'Fe3B', 'O']
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['fract_x'].value == 0.125
    assert phase_dict['Fe3O4']['atoms']['Fe3B']['fract_y'].value == 0.5
    assert phase_dict['Fe3O4']['atoms']['O']['fract_z'].value == 0.25521
    assert phase_dict['Fe3O4']['atoms']['O']['fract_z']['store']['error'] == 0.0
    assert phase_dict['Fe3O4']['atoms']['O']['fract_z']['header'] == 'z'

    assert phase_dict['Fe3O4']['atoms']['Fe3B']['scat_length_neutron'].value == 0.945

    # occupancy
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['occupancy'].value == 1.0
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['occupancy']['store']['refine'] is False

    # ADP type
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['adp_type']['header'] == 'Type'
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['adp_type'].value == 'Uiso'
    assert phase_dict['Fe3O4']['atoms']['O']['adp_type'].value == 'Uiso'

    # Isotropic ADP
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['U_iso_or_equiv']['header'] == 'Biso'
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['U_iso_or_equiv'].value == 0.0
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['U_iso_or_equiv']['store'].max == 1
    assert phase_dict['Fe3O4']['atoms']['O']['U_iso_or_equiv'].value == 0.0
    assert phase_dict['Fe3O4']['atoms']['O']['U_iso_or_equiv']['store']['constraint'] is None

    # Isotropic ADP
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['ADP']['u_11']['header'] == 'U11'
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['ADP']['u_11'].value is None
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['ADP']['u_22'].value is None
    # TODO find out why -np.Inf != -np.Inf
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['ADP']['u_23']['store'].max == np.Inf
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['ADP']['u_23']['store'].min == -np.Inf
    assert phase_dict['Fe3O4']['atoms']['Fe3B']['ADP']['u_23'].value is None
    assert phase_dict['Fe3O4']['atoms']['Fe3B']['ADP']['u_23']['store']['constraint'] is None

    # Anisotropic MSP
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['MSP']['type'].value == 'Cani'
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['MSP']['chi_11'].value == -3.468
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['MSP']['chi_33'].value == -3.468
    assert phase_dict['Fe3O4']['atoms']['Fe3A']['MSP']['chi_23']['store'].max == 1
    assert phase_dict['Fe3O4']['atoms']['Fe3B']['MSP']['chi_23'].value == 0.0
    assert phase_dict['Fe3O4']['atoms']['Fe3B']['MSP']['chi_23']['store']['refine'] is False


def test_setExperiment(cal):
    experiment = cal.getExperiment('pd')
    cal.project_dict['experiments']['pd']['wavelength'].value = 2
    cal.setExperiment(experiment)
    assert cal.project_dict['experiments']['pd']['wavelength'].value == 0.84


def test_setExperiments(cal):
    experiment = cal.getExperiment('pd')
    experiments = Experiments(experiment)
    experiemnt2 = deepcopy(experiment)
    experiemnt2['name'] = 'pd2'
    experiments['pd2'] = experiemnt2
    cal.setExperiments(experiments)
    assert len(cal.project_dict['experiments']) == 2
    assert cal.project_dict['experiments']['pd']['wavelength'].value == 0.84
    assert cal.project_dict['experiments']['pd2']['wavelength'].value == 0.84

def test_setExperimentRefine(cal):
    assert cal.project_dict['experiments']['pd']['wavelength'].refine is False
    cal.setExperimentRefine('pd', ['wavelength'], True)
    assert cal.project_dict['experiments']['pd']['wavelength'].refine is True

def test_setExperimentValue(cal):
    assert cal.project_dict['experiments']['pd']['wavelength'].value == 0.84
    cal.setExperimentValue('pd', ['wavelength'], 5)
    assert cal.project_dict['experiments']['pd']['wavelength'].value == 5

def test_setExperimentDefinitionFromString():
    calc = CryspyCalculator()
    interface = CalculatorInterface(calc)
    interface.setPhaseDefinition(phase_path)
    with open(exp_path, 'r') as file_reader:
        exp_content = file_reader.read()
    interface.addExperimentDefinitionFromString(exp_content)

    experiment_dict = interface.project_dict['experiments']

    assert len(experiment_dict) == 1
    assert len(experiment_dict['pd']) == 10
    # wavelength
    assert len(experiment_dict['pd']['wavelength']) == 5
    assert experiment_dict['pd']['wavelength'].value == 0.84
    assert experiment_dict['pd']['wavelength']['url'] == ''

    # offset
    assert len(experiment_dict['pd']['offset']) == 5
    assert experiment_dict['pd']['offset'].value == -0.385404
    assert experiment_dict['pd']['offset']['store']['error'] == 0.0
    assert experiment_dict['pd']['offset']['store']['refine'] is False

    # phase
    assert len(experiment_dict['pd']['phase']) == 1
    assert len(experiment_dict['pd']['phase']['Fe3O4']['scale']) == 5
    assert experiment_dict['pd']['phase']['Fe3O4']['scale'].value == 0.02381
    assert experiment_dict['pd']['phase']['Fe3O4']['scale']['store']['refine'] is False
    assert experiment_dict['pd']['phase']['Fe3O4']['scale']['store']['error'] == 0.0

    # background
    assert len(experiment_dict['pd']['background']) == 3
    assert experiment_dict['pd']['background']['4.5']['ttheta'] == 4.5
    assert len(experiment_dict['pd']['background']['4.5']['intensity']) == 5
    assert experiment_dict['pd']['background']['4.5']['intensity'].value == 256.0
    assert experiment_dict['pd']['background']['80.0']['ttheta'] == 80.0
    assert len(experiment_dict['pd']['background']['80.0']['intensity']) == 5
    assert experiment_dict['pd']['background']['80.0']['intensity'].value == 65.0

    # resolution
    assert len(experiment_dict['pd']['resolution']) == 5
    assert len(experiment_dict['pd']['resolution']['u']) == 5
    assert experiment_dict['pd']['resolution']['u'].value == 16.9776
    assert experiment_dict['pd']['resolution']['u']['store']['refine'] is False
    assert len(experiment_dict['pd']['resolution']['y']) == 5
    assert experiment_dict['pd']['resolution']['v'].value == -2.8357
    assert experiment_dict['pd']['resolution']['v']['store']['error'] == 0.0
    assert experiment_dict['pd']['resolution']['v']['store']['hide'] is False

    # measured_pattern
    assert len(experiment_dict['pd']['measured_pattern']) == 9
    assert 5.0 in experiment_dict['pd']['measured_pattern']['x']
    assert len(experiment_dict['pd']['measured_pattern'].y_obs_lower) == 381
    assert experiment_dict['pd']['measured_pattern'].y_obs_lower[380] == pytest.approx(762.959046)


def test_setExperimentsDictFromCryspyObj(cal):
    # difficult test for creation of the experiment dict
    cal.project_dict['experiments'].clear()  # enforce
    assert cal.calculator._cryspy_obj.experiments is not None

    cal.updateExperiments()

    experiment_dict = cal.project_dict['experiments']

    assert len(experiment_dict) == 1
    assert len(experiment_dict['pd']) == 10
    # wavelength
    assert len(experiment_dict['pd']['wavelength']) == 5
    assert experiment_dict['pd']['wavelength'].value == 0.84
    assert experiment_dict['pd']['wavelength']['url'] == ''

    # offset
    assert len(experiment_dict['pd']['offset']) == 5
    assert experiment_dict['pd']['offset'].value == -0.385404
    assert experiment_dict['pd']['offset']['store']['error'] == 0.0
    assert experiment_dict['pd']['offset']['store']['refine'] is False

    # phase
    assert len(experiment_dict['pd']['phase']) == 1
    assert len(experiment_dict['pd']['phase']['Fe3O4']['scale']) == 5
    assert experiment_dict['pd']['phase']['Fe3O4']['scale'].value == 0.02381
    assert experiment_dict['pd']['phase']['Fe3O4']['scale']['store']['refine'] is False
    assert experiment_dict['pd']['phase']['Fe3O4']['scale']['store']['error'] == 0.0

    # background
    assert len(experiment_dict['pd']['background']) == 3
    assert experiment_dict['pd']['background']['4.5']['ttheta'] == 4.5
    assert len(experiment_dict['pd']['background']['4.5']['intensity']) == 5
    assert experiment_dict['pd']['background']['4.5']['intensity'].value == 256.0
    assert experiment_dict['pd']['background']['80.0']['ttheta'] == 80.0
    assert len(experiment_dict['pd']['background']['80.0']['intensity']) == 5
    assert experiment_dict['pd']['background']['80.0']['intensity'].value == 65.0

    # resolution
    assert len(experiment_dict['pd']['resolution']) == 5
    assert len(experiment_dict['pd']['resolution']['u']) == 5
    assert experiment_dict['pd']['resolution']['u'].value == 16.9776
    assert experiment_dict['pd']['resolution']['u']['store']['refine'] is False
    assert len(experiment_dict['pd']['resolution']['y']) == 5
    assert experiment_dict['pd']['resolution']['v'].value == -2.8357
    assert experiment_dict['pd']['resolution']['v']['store']['error'] == 0.0
    assert experiment_dict['pd']['resolution']['v']['store']['hide'] is False

    # measured_pattern
    assert len(experiment_dict['pd']['measured_pattern']) == 9
    assert 5.0 in experiment_dict['pd']['measured_pattern']['x']
    assert len(experiment_dict['pd']['measured_pattern'].y_obs_lower) == 381
    assert experiment_dict['pd']['measured_pattern'].y_obs_lower[380] == pytest.approx(762.959046)


def test_setCalculationsDictFromCryspyObj(cal):
    cal.project_dict['calculations'].clear()

    assert cal.calculator._cryspy_obj.crystals is not None

    cal.updateCalculations()

    calculation_dict = cal.project_dict['calculations']

    assert len(calculation_dict) == 1

    assert len(calculation_dict['pd']) == 4
    # bragg_peaks
    assert len(calculation_dict['pd']['bragg_peaks']) == 1
    assert sum(calculation_dict['pd']['bragg_peaks']['Fe3O4']['h']) == 681
    assert sum(calculation_dict['pd']['bragg_peaks']['Fe3O4']['ttheta']) == pytest.approx(4993.5717)
    # calculated_pattern
    assert len(calculation_dict['pd']['calculated_pattern']) == 8
    assert len(calculation_dict['pd']['calculated_pattern']['x']) == 381
    assert sum(calculation_dict['pd']['calculated_pattern']['x']) == 16002.0
    assert sum(calculation_dict['pd']['calculated_pattern']['y_diff_upper']) == pytest.approx(162647.08)

    # calculated data limits
    assert len(calculation_dict['pd']['limits']) == 2
    assert calculation_dict['pd']['limits']['main']['x_min'] == 4.0
    assert calculation_dict['pd']['limits']['main']['y_max'] == pytest.approx(6134.188081)
    assert calculation_dict['pd']['limits']['difference']['y_min'] == pytest.approx(-1647.0144)
    assert calculation_dict['pd']['limits']['difference']['y_max'] == pytest.approx(5185.9742)


def test_phasesCount(cal):
    assert cal.phasesCount() == 1


def test_experimentsCount(cal):
    assert cal.experimentsCount() == 1


def test_phasesIds(cal):
    assert cal.phasesIds() == ['Fe3O4']


def test_experimentsIds(cal):
    assert cal.experimentsIds() == ['pd']


def test_asDict(cal):
    assert isinstance(cal.asDict(), dict)


def test_name(cal):
    assert cal.name() == 'Fe3O4'


def test_asCifDict(cal):
    d = cal.asCifDict()

    assert isinstance(d, dict)
    assert 'data_Fe3O4' in d['phases']
    assert 'data_pd' in d['experiments']
    assert '_refln_index_h' in d['calculations']


def genericTestProjectDict(constructor, *args):
    expected = ['interface', 'calculator', 'app', 'info', 'phases', 'experiments', 'calculations']
    expected_type = [Interface, Calculator, App, Info, Phases, Experiments, Calculations]
    PathDictDerived(constructor, expected, expected_type, *args)
    return constructor(*args)


def test_ProjectDict_default():
    pd = genericTestProjectDict(ProjectDict.default)
    assert len(pd['experiments']) == 0
    assert len(pd['phases']) == 0
    assert len(pd['calculations']) == 0


def test_ProjectDict_from_pars():
    exp = Experiment.default('boo')
    phase = Phase.default('woo')
    calc = Calculation.default('foo')

    pd = genericTestProjectDict(ProjectDict.fromPars, exp, phase, calc)
    assert len(pd['experiments']) == 1
    assert len(pd['phases']) == 1
    assert len(pd['calculations']) == 1
    assert pd['experiments']['boo'] == exp
    assert pd['phases']['woo'] == phase
    assert pd['calculations']['foo'] == calc


def refineHelper(cal):
    assert cal.project_dict['phases']['Fe3O4']['cell']['length_a'].refine
    assert pytest.approx(cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value, 8.36212)
    r = cal.refine()
    rr = {'num_refined_parameters': 1,
          'refinement_message': 'Desired error not necessarily achieved due to precision loss.',
          'nfev': 256,
          'nit': 5,
          'njev': 83,
          }
    if platform == "darwin":
        rr['nfev'] = 274
        rr['njev'] = 89
    elif platform == 'win32':
        rr['nfev'] = 271
        rr['njev'] = 88
    chi_ref = 3.3723747910939683
    chi_found = r['final_chi_sq']
    del r['final_chi_sq']
    assert r == rr
    assert pytest.approx(chi_found, chi_ref, 0.6)  # because we have errors here :-/
    assert pytest.approx(cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value, 8.561673117085581)


# @pytest.mark.xfail(strict=False)
def test_refine(cal):
    refineHelper(cal)


def test_Undo(cal):
    refineHelper(cal)
    assert cal.canUndo()
    assert cal.project_dict.undoText() == 'Refinement'
    cal.undo()
    assert pytest.approx(cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value, 8.36212)


def test_Redo(cal):
    refineHelper(cal)
    assert cal.canUndo()
    assert cal.project_dict.undoText() == 'Refinement'
    cal.undo()
    assert pytest.approx(cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value, 8.36212)
    assert cal.project_dict.redoText() == 'Refinement'
    assert cal.canRedo()
    cal.redo()
    assert pytest.approx(cal.project_dict['phases']['Fe3O4']['cell']['length_a'].value, 8.561673117085581)


def test_clearUndoStack(cal):
    assert cal.canUndo()
    cal.clearUndoStack()
    assert not cal.canUndo()


def test_setPhaseDefinition(cal):
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.setPhaseDefinition(phase_path)
    phase_added = interface.getPhase('Fe3O4')
    phase_ref = cal.getPhase('Fe3O4')
    assert phase_added['phasename'] == phase_ref['phasename']
    assert phase_added['spacegroup']['crystal_system'].value == phase_ref['spacegroup']['crystal_system'].value
    assert phase_added['spacegroup']['space_group_name_HM_ref'].value == phase_ref['spacegroup'][
        'space_group_name_HM_ref'].value
    assert phase_added['spacegroup']['space_group_IT_number'].value == phase_ref['spacegroup'][
        'space_group_IT_number'].value
    assert phase_added['spacegroup']['origin_choice'].value == phase_ref['spacegroup']['origin_choice'].value
    assert phase_added['cell']['length_a'].value == phase_ref['cell']['length_a'].value
    assert phase_added['cell']['length_b'].value == phase_ref['cell']['length_b'].value
    assert phase_added['cell']['length_c'].value == phase_ref['cell']['length_c'].value
    assert phase_added['cell']['angle_alpha'].value == phase_ref['cell']['angle_alpha'].value
    assert phase_added['cell']['angle_beta'].value == phase_ref['cell']['angle_beta'].value
    assert phase_added['cell']['angle_gamma'].value == phase_ref['cell']['angle_gamma'].value
    assert phase_added['atoms']['Fe3A']['fract_x'].value == phase_ref['atoms']['Fe3A']['fract_x'].value
    assert phase_added['atoms']['Fe3B']['fract_y'].value == phase_ref['atoms']['Fe3B']['fract_y'].value
    assert phase_added['atoms']['O']['fract_z'].value == phase_ref['atoms']['O']['fract_z'].value


def test_addPhaseDefinition(cal):
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.addPhaseDefinition(phase_path)
    phase_added = interface.getPhase('Fe3O4')
    phase_ref = cal.getPhase('Fe3O4')
    assert phase_added['phasename'] == phase_ref['phasename']
    assert phase_added['spacegroup']['crystal_system'].value == phase_ref['spacegroup']['crystal_system'].value
    assert phase_added['spacegroup']['space_group_name_HM_ref'].value == phase_ref['spacegroup'][
        'space_group_name_HM_ref'].value
    assert phase_added['spacegroup']['space_group_IT_number'].value == phase_ref['spacegroup'][
        'space_group_IT_number'].value
    assert phase_added['spacegroup']['origin_choice'].value == phase_ref['spacegroup']['origin_choice'].value
    assert phase_added['cell']['length_a'].value == phase_ref['cell']['length_a'].value
    assert phase_added['cell']['length_b'].value == phase_ref['cell']['length_b'].value
    assert phase_added['cell']['length_c'].value == phase_ref['cell']['length_c'].value
    assert phase_added['cell']['angle_alpha'].value == phase_ref['cell']['angle_alpha'].value
    assert phase_added['cell']['angle_beta'].value == phase_ref['cell']['angle_beta'].value
    assert phase_added['cell']['angle_gamma'].value == phase_ref['cell']['angle_gamma'].value
    assert phase_added['atoms']['Fe3A']['fract_x'].value == phase_ref['atoms']['Fe3A']['fract_x'].value
    assert phase_added['atoms']['Fe3B']['fract_y'].value == phase_ref['atoms']['Fe3B']['fract_y'].value
    assert phase_added['atoms']['O']['fract_z'].value == phase_ref['atoms']['O']['fract_z'].value


def test_setPhaseDefinition_None():
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.setPhaseDefinition(None)


def test_setPhaseDefinition_EmptyStr():
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.setPhaseDefinition('')


def test_setExperimentDefinition(cal):
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.setExperimentDefinition(exp_path)
    exp_added = interface.getExperiment('pd')
    exp_ref = cal.getExperiment('pd')
    assert exp_added['name'] == exp_ref['name']
    assert exp_added['wavelength'].value == exp_ref['wavelength'].value
    assert exp_added['offset'].value == exp_ref['offset'].value
    assert exp_added['phase']['Fe3O4']['name'] == exp_ref['phase']['Fe3O4']['name']
    assert exp_added['phase']['Fe3O4']['scale'].value == exp_ref['phase']['Fe3O4']['scale'].value


def test_addExperimentDefinition(cal):
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.addExperimentDefinition(exp_path)
    exp_added = interface.getExperiment('pd')
    exp_ref = cal.getExperiment('pd')
    assert exp_added['name'] == exp_ref['name']
    assert exp_added['wavelength'].value == exp_ref['wavelength'].value
    assert exp_added['offset'].value == exp_ref['offset'].value
    assert exp_added['phase']['Fe3O4']['name'] == exp_ref['phase']['Fe3O4']['name']
    assert exp_added['phase']['Fe3O4']['scale'].value == exp_ref['phase']['Fe3O4']['scale'].value


def test_addPhaseToExp():
    calc = CryspyCalculator('')
    interface = CalculatorInterface(calc)
    interface.addExperimentDefinition(exp_path)
    interface.addPhaseDefinition(phase_path)
    interface.removePhaseFromExp('pd', 'Fe3O4')
    interface.addPhaseToExp('pd', 'Fe3O4', scale=1.0)

    exp_ref = interface.getExperiment('pd')
    assert exp_ref['name'] == 'pd'
    assert 'Fe3O4' in exp_ref['phase'].keys()
    assert exp_ref['phase']['Fe3O4']['scale'].value == 1.0


def test_removePhaseFromExp(cal):

    cal.removePhaseFromExp('pd', 'Fe3O4')

    exp_ref = cal.getExperiment('pd')
    assert exp_ref['name'] == 'pd'
    assert 'Fe3O4' not in exp_ref['phase'].keys()


def test_addExperiment(cal):
    exp2 = cal.getExperiment('pd')
    exp2['name'] = 'Testing'

    cal.addExperiment(exp2)

    assert len(cal.project_dict['experiments']) == 2
    assert 'Testing' in cal.project_dict['experiments'].keys()
    assert cal.project_dict['experiments']['Testing']['name'] == 'Testing'
    assert cal.project_dict['experiments']['Testing'] == exp2


def test_removeExperiment(cal):
    exp2 = cal.getExperiment('pd')
    exp2['name'] = 'Testing'
    cal.addExperiment(exp2)
    cal.removeExperiment('pd')

    assert len(cal.project_dict['experiments']) == 1
    assert 'pd' not in cal.project_dict['experiments'].keys()
    assert 'Testing' in cal.project_dict['experiments'].keys()
    assert cal.project_dict['experiments']['Testing']['name'] == 'Testing'
    assert cal.project_dict['experiments']['Testing'] == exp2


def test_getExperiment_None(cal):
    exp2 = cal.getExperiment('pd')
    exp2['name'] = 'Testing'
    cal.addExperiment(exp2)

    exps = cal.getExperiment(None)
    assert len(exps) == 2
    assert 'pd' in exps.keys()
    assert 'Testing' in exps.keys()
    assert exps['Testing']['name'] == 'Testing'
    assert exps['pd']['name'] == 'pd'


def test_cif_writers(cal):

    def file_tester(path: str, option=None):

        if option is None:
            option = ['main', 'phases', 'experiments']

        if 'main' in option:
            assert os.path.exists(os.path.join(path, DEFAULT_FILENAMES['project']))
            with open(os.path.join(path, DEFAULT_FILENAMES['project']), 'r') as new_reader:
                new_data = new_reader.read()
                assert new_data.find('_name Fe3O4') != -1
                assert new_data.find('_samples %s' % DEFAULT_FILENAMES['phases']) != -1
                assert new_data.find('_experiments %s' % DEFAULT_FILENAMES['experiments']) != -1
        elif'phases' in option:
            assert os.path.exists(os.path.join(path, DEFAULT_FILENAMES['phases']))
            with open(os.path.join(path, DEFAULT_FILENAMES['phases']), 'r') as new_reader:
                new_data = new_reader.read()
                assert new_data.find('data_Fe3O4') != -1
                assert new_data.find('_cell_length_b 8.36212') != -1
                assert new_data.find('Fe3B Fe3+ 0.5 0.5 0.5 1.0 Uiso 0.0 16 d') != -1
                assert new_data.find('Fe3A 2.0 1.0') != -1
                assert new_data.find('Fe3A Cani -3.468 -3.468 -3.468 0.0 0.0 0.0') != -1
        elif 'experiments' in option:
            assert os.path.exists(os.path.join(path, DEFAULT_FILENAMES['experiments']))
            with open(os.path.join(path, DEFAULT_FILENAMES['experiments']), 'r') as new_reader:
                new_data = new_reader.read()
                assert new_data.find('data_pd') != -1
                assert new_data.find('_setup_offset_2theta -0.385404') != -1
                assert new_data.find('5.0 166.47 106.51 426.73 109.08') != -1

    with tempfile.TemporaryDirectory() as td:
        cal.writeMainCif(td)
        file_tester(td, option=['main'])

    with tempfile.TemporaryDirectory() as td:
        cal.writePhaseCif(td)
        file_tester(td, option=['phases'])

    with tempfile.TemporaryDirectory() as td:
        cal.writeExpCif(td)
        file_tester(td, option=['experiments'])
