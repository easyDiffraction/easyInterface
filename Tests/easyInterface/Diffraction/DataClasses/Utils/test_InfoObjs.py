import pytest
from easyInterface.Diffraction.DataClasses.Utils.InfoObjs import *
from Tests.easyInterface.Diffraction.DataClasses.Utils.Helpers import PathDictDerived


def test_Info_Default():
    expected = ['name', 'phase_ids', 'experiment_ids', 'modified_datetime', 'refinement_datetime', 
                'chi_squared', 'n_res']
    expected_type = [str, list, list, str, str, Base, Base]
    PathDictDerived(Info.default, expected, expected_type)


def test_calculator():
    info = Calculator()
    assert isinstance(info, PathDict)
    keys = info.keys()
    assert 'name' in keys
    assert info['name'] == 'CrysPy'
    assert 'version' in keys
    assert 'url' in keys


def test_interface():
    info = Calculator()
    assert isinstance(info, PathDict)
    keys = info.keys()
    assert 'name' in keys
    assert info['name'] == 'CrysPy'
    assert 'version' in keys
    assert 'url' in keys