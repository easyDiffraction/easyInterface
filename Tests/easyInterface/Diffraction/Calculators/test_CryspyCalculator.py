import pytest
# module for testing
from easyInterface import logger, logging
logger.addSysOutput()
logger.setLevel(logging.DEBUG)
from easyInterface.Diffraction.Calculators import CryspyCalculator

file_path = "Tests/Data/main.cif"
fitdata_data = [0, 2, 3, 5]

def test_creationEmptyFile():
    calc = CryspyCalculator('baah')
    assert calc._phase_name == []
    
def test_calculator_info():
    info = CryspyCalculator.calculatorInfo()
    assert isinstance(info, dict)
    keys = info.keys()
    assert 'name' in keys
    assert info['name'] == 'CrysPy'
    assert 'version' in keys
    assert 'url' in keys



@pytest.fixture
def cal():
    calc = CryspyCalculator(file_path)
    return calc


def test__create_cryspy_obj(cal):
    assert True


def test__parse_segment(cal):
    assert True

@pytest.mark.skip
def test_set_exps_definition(cal):
    file = "Tests/Data/experiments.cif"
    cal.setExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 1
    assert cal._experiments_path == file
@pytest.mark.skip
def test_add_exps_definition(cal):
    file = "Tests/Data/experiments2.cif"
    cal.addExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 2


def test_remove_exps_definition(cal):
    assert True


def test_set_phase_definition(cal):
    """
    Load another phase file and check if the content is correctly updated
    """
    NEW_PHASE_FILE = "Tests/Data/phases_2.cif"
    file_path = NEW_PHASE_FILE
    cal.setPhaseDefinition(file_path)
    assert 'Fe2Co1O4' in cal.getPhaseNames()

def test_add_phase_definition(cal):
    assert True


def test_remove_phase_definition(cal):
    assert True


def test_write_main_cif(cal):
    assert True


def test_write_phase_cif(cal):
    assert True


def test_write_exp_cif(cal):
    assert True


def test_save_cifs(cal):
    assert True


def test__create_proj_item_from_obj(cal):
    assert True


def test_get_phases(cal):
    assert True


def test_get_experiments(cal):
    assert True


def test_get_calculations(cal):
    assert True


def test__set_calculator_obj_from_project_dict(cal):
    assert True


def test__create_proj_dict_from_obj(cal):
    assert True


def test_set_phases(cal):
    assert True


def test_set_experiments(cal):
    assert True


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
    assert True
