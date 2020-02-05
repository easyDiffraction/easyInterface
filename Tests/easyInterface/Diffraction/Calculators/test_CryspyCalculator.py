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


def test_caclulatorInfo():
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

@pytest.mark.skip
def test_setExpsDefinition(cal):
    file = "Tests/Data/experiments.cif"
    cal.setExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 1
    assert cal._experiments_path == file

@pytest.mark.skip
def test_addExpsDefinition(cal):
    file = "Tests/Data/experiments2.cif"
    cal.addExpsDefinition(file)
    assert len(cal._cryspy_obj.experiments) == 2


def test_updatePhases(cal):
    """
    Load another phase file and check if the content is correctly updated
    """
    NEW_PHASE_FILE = "Tests/Data/phases_2.cif"
    file_path = NEW_PHASE_FILE
    cal.setPhaseDefinition(file_path)
    assert 'Fe2Co1O4' in cal.getPhaseNames()
