import os
import tempfile

import pytest

from easyInterface import logger, logging

logger.addSysOutput()
logger.setLevel(logging.DEBUG)

from easyInterface.Diffraction.Calculators import CryspyCalculator

test_data = os.path.join("tests", "Data")
file_path = os.path.join(test_data, 'main.cif')


@pytest.fixture
def cal():
    calc = CryspyCalculator(file_path)
    return calc


@pytest.fixture
def file_io_fixture():
    created_files = []

    def _file_io_fixture(save_dir: str, filename: str):
        save_to = os.path.join(save_dir, filename)
        if os.path.exists(save_to):
            os.remove(save_to)
        created_files.append(save_to)
        return save_to

    yield _file_io_fixture

    for file in created_files:
        if os.path.exists(file):
            os.remove(file)


def test_creationEmptyFile():
    calc = CryspyCalculator('baah')
    assert calc._phase_names == []


def test_calculator_info():
    info = CryspyCalculator.calculatorInfo()
    assert isinstance(info, dict)
    keys = info.keys()
    assert 'name' in keys
    assert info['name'] == 'CrysPy'
    assert 'version' in keys
    assert 'url' in keys


def test__create_cryspy_obj(cal):
    assert cal._cryspy_obj
    assert len(cal._cryspy_obj.experiments) == 1
    assert len(cal._cryspy_obj.crystals) == 1


def test__parse_segment(cal):
    assert True

def test_addExpDefinitionFromString(cal):
    file = os.path.join(test_data, 'experiments.cif')

    with open(file, 'r') as file_reader:
        exp_str = file_reader.read()
    cal.addExpDefinitionFromString(exp_str)
    assert len(cal._cryspy_obj.experiments) == 2


def test_set_exps_definition(cal):
    file = os.path.join(test_data, 'experiments.cif')
    cal.setExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 1
    assert cal._experiments_path == file
    assert cal._experiment_names == ['pd']


def test_add_exps_definition(cal):
    file = os.path.join(test_data, 'experiments2.cif')
    cal.addExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 2
    assert cal._experiment_names == ['pd', 'pd2']


def test_remove_exps_definition(cal):
    cal.removeExpsDefinition('pd')
    assert cal._cryspy_obj.experiments is None
    assert cal._experiment_names == []


def test_set_phase_definition(cal):
    """
    Load another phase file and check if the content is correctly updated
    """
    NEW_PHASE_FILE = os.path.join(test_data, 'phases_2.cif')
    file_path = NEW_PHASE_FILE
    cal.setPhaseDefinition(file_path)
    assert 'Fe2Co1O4' in cal._phase_names
    assert len(cal._cryspy_obj.crystals) == 1


def test_add_phase_definition(cal):
    file = os.path.join(test_data, 'phases_2.cif')
    cal.addPhaseDefinition(file)
    assert len(cal._phase_names) == 2
    assert len(cal._cryspy_obj.crystals) == 2
    assert cal._phase_names == ['Fe3O4', 'Fe2Co1O4']


def test_remove_phase_definition(cal):
    cal.removePhaseDefinition('Fe3O4')
    assert cal._cryspy_obj.crystals is None
    assert cal._phase_names == []


def test_write_main_cif(cal, file_io_fixture):
    out_file = test_data
    filename = 'main_testing.cif'

    save_to = file_io_fixture(out_file, filename)
    cal.writeMainCif(out_file, filename)
    assert os.path.exists(save_to)


def test_write_phase_cif(cal, file_io_fixture):
    out_file = test_data
    filename = 'phases_testing.cif'
    save_to = file_io_fixture(out_file, filename)
    cal.writePhaseCif(out_file, filename)
    assert os.path.exists(save_to)


def test_write_exp_cif(cal, file_io_fixture):
    out_file = test_data
    filename = 'experiments_testing.cif'
    save_to = file_io_fixture(out_file, filename)
    cal.writeExpCif(out_file, filename)
    assert os.path.exists(save_to)


def test_save_cifs(cal, file_io_fixture):
    out_file = test_data
    main_filename = 'main_testing.cif'
    main_save_to = file_io_fixture(out_file, main_filename)
    phases_filename = 'phases_testing.cif'
    phases_save_to = file_io_fixture(out_file, phases_filename)
    exps_filename = 'experiments_testing.cif'
    exps_save_to = file_io_fixture(out_file, exps_filename)
    cal.saveCifs(out_file, main_filename, exps_filename, phases_filename)
    assert os.path.exists(main_save_to)
    assert os.path.exists(phases_save_to)
    assert os.path.exists(exps_save_to)


def test__create_proj_item_from_obj(cal):
    assert True


def test_get_phases(cal):
    phases = cal.getPhases()
    assert len(phases) == len(cal._cryspy_obj.crystals)
    # Spacegroup
    assert phases.getItemByPath(['Fe3O4', 'spacegroup', 'origin_choice']).value == '2'
    assert phases.getItemByPath(['Fe3O4', 'spacegroup', 'space_group_name_HM_alt']).value == 'F d -3 m'
    # Cell
    assert phases.getItemByPath(['Fe3O4', 'cell', 'length_a']).value == 8.36212
    assert phases.getItemByPath(['Fe3O4', 'cell', 'length_a']).value == phases.getItemByPath(
        ['Fe3O4', 'cell', 'length_b']).value
    assert phases.getItemByPath(['Fe3O4', 'cell', 'length_a']).value == phases.getItemByPath(
        ['Fe3O4', 'cell', 'length_c']).value
    assert phases.getItemByPath(['Fe3O4', 'cell', 'angle_alpha']).value == 90
    # Atoms
    assert phases.getItemByPath(['Fe3O4', 'atoms', 'Fe3A', 'fract_x']).value == 0.125
    assert phases.getItemByPath(['Fe3O4', 'atoms', 'Fe3B', 'fract_y']).value == 0.5
    assert phases.getItemByPath(['Fe3O4', 'atoms', 'O', 'fract_z']).value == 0.25521

    assert phases.getItemByPath(['Fe3O4', 'cell', 'length_a']).refine
    assert not phases.getItemByPath(['Fe3O4', 'cell', 'length_c']).refine


def test_get_experiments(cal):
    experiments = cal.getExperiments()
    assert len(experiments) == len(cal._cryspy_obj.experiments)
    assert 'pd' in experiments.keys()
    assert experiments.getItemByPath(['pd', 'wavelength']).value == 0.84
    assert experiments.getItemByPath(['pd', 'offset']).value == -0.385404
    assert len(experiments.getItemByPath(['pd', 'background'])) == 3
    assert '40.0' in experiments.getItemByPath(['pd', 'background']).keys()
    assert experiments.getItemByPath(['pd', 'background', '40.0', 'ttheta']) == 40.0
    assert experiments.getItemByPath(['pd', 'background', '40.0', 'intensity']).value == 158.0
    assert experiments.getItemByPath(['pd', 'resolution', 'u']).value == 16.9776
    assert experiments.getItemByPath(['pd', 'resolution', 'w']).value == 0.5763
    assert sum(experiments.getItemByPath(['pd', 'measured_pattern', 'x'])) == 16002.0
    assert pytest.approx(sum(experiments.getItemByPath(['pd', 'measured_pattern', 'y_obs'])), 389605.38)


def test_get_calculations(cal):
    calculations = cal.getCalculations()
    assert 'pd' in calculations.keys()
    assert calculations['pd']['name'] == 'pd'
    assert sum(calculations['pd']['calculated_pattern']['x']) == 16002.0
    assert pytest.approx(calculations['pd']['calculated_pattern']['y_calc'], 370866.19168)
    assert calculations['pd']['limits']['main']['x_min'] == 4.0
    assert calculations['pd']['limits']['main']['x_max'] == 80.0
    assert pytest.approx(calculations['pd']['limits']['main']['y_min'], 102.0307)
    assert pytest.approx(calculations['pd']['limits']['main']['y_max'], 6134.1881)
    assert pytest.approx(calculations['pd']['limits']['difference']['y_min'], -4087.48284)
    assert pytest.approx(calculations['pd']['limits']['difference']['y_max'], 4601.62523)


def test__set_calculator_obj_from_project_dict(cal):
    assert True


def test__create_proj_dict_from_obj(cal):
    assert True


def test_set_phases(cal):
    from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases
    import copy
    phases = cal.getPhases()
    try:
        phase = copy.deepcopy(phases['Fe3O4'])
    except TypeError:
        # Travis doesn't like deepcopy :-/
        phase = phases['Fe3O4']
    phase['atoms']['Fe3A']['fract_x'].value = 0.2
    phases = Phases(phase)
    cal.setPhases(phases)
    phases = cal.getPhases()
    assert len(phases) == 1
    assert phases.getItemByPath(['Fe3O4', 'atoms', 'Fe3A', 'fract_x']).value == 0.2


def test_set_experiments(cal):
    from easyInterface.Diffraction.DataClasses.DataObj.Experiment import Experiments
    import copy
    experiments = cal.getExperiments()
    try:
        experiment = copy.deepcopy(experiments['pd'])
    except TypeError:
        # Travis doesn't like deepcopy :-/
        experiment = experiments['pd']
    experiment['measured_pattern']['y_obs'][0] = 500
    experiments = Experiments(experiment)
    cal.setExperiments(experiments)
    experiments = cal.getExperiments()
    assert len(experiments) == 1
    assert experiments.getItemByPath(['pd', 'measured_pattern', 'y_obs'])[0] == 500


def test_set_obj_from_project_dicts(cal):
    assert True


def test_as_cif_dict(cal):
    assert True


def test_refine(cal):
    assert True


def test_get_chi_sq(cal):
    assert True


def test_final_chi_square(cal):
    assert True


def test__mapped_value_updater(cal):
    assert True


def test__mapped_refine_updater(cal):
    assert True


def test_get_project_name(cal):
    assert True


def test_get_phase_names(cal):
    assert True


def test_add_phase(cal):
    phases = cal.getPhases()
    import copy
    phase = copy.deepcopy(phases['Fe3O4'])
    phase['phasename'] = 'FeBoop'
    from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases
    phases = Phases([phases['Fe3O4'], phase])
    cal.setPhases(phases)
    assert len(phases) == 2


def test_cif_writers(cal):

    def file_tester(path: str, option=None):

        if option is None:
            option = ['main', 'phases', 'experiments']

        if 'main' in option:
            assert os.path.exists(os.path.join(path, 'main.cif'))
            with open(os.path.join(path, 'main.cif'), 'r') as new_reader:
                new_data = new_reader.read()
                assert new_data.find('_name Fe3O4') != -1
                assert new_data.find('_phases phases.cif') != -1
                assert new_data.find('_experiments experiments.cif') != -1
        elif'phases' in option:
            assert os.path.exists(os.path.join(path, 'phases.cif'))
            with open(os.path.join(path, 'phases.cif'), 'r') as new_reader:
                new_data = new_reader.read()
                assert new_data.find('data_Fe3O4') != -1
                assert new_data.find('_cell_length_b 8.56212') != -1
                assert new_data.find('Fe3B Cani 3.041 3.041 3.041 0.0 0.0 0.0') != -1
                assert new_data.find('Fe3A 2.0 1.0 ') != -1
                assert new_data.find('Fe3A Fe3+ 0.125 0.125 0.125 1.0 Uiso 0.0') != -1
        elif 'experiments' in option:
            assert os.path.exists(os.path.join(path, 'experiments.cif'))
            with open(os.path.join(path, 'experiments.cif'), 'r') as new_reader:
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