from easyInterface.Common.PhaseObj.SpaceGroup import *
from tests.easyInterface.Common.Utils.Helpers import PathDictDerived


def genericTestSG(sg_constructor, *args):
    expected = ['crystal_system', 'space_group_name_HM_alt', 'space_group_IT_number', 'origin_choice']

    expected_type = [Base, Base, Base, Base]
    PathDictDerived(sg_constructor, expected, expected_type, *args)

    sg = sg_constructor(*args)

    assert sg.getItemByPath(['crystal_system', 'header']) == SG_DETAILS['crystal_system']['header']
    assert sg.getItemByPath(['space_group_name_HM_alt', 'header']) == SG_DETAILS['space_group_name_HM_alt']['header']
    assert sg.getItemByPath(['space_group_IT_number', 'header']) == SG_DETAILS['space_group_IT_number']['header']
    assert sg.getItemByPath(['origin_choice', 'header']) == SG_DETAILS['origin_choice']['header']

    assert sg.getItemByPath(['crystal_system', 'tooltip']) == SG_DETAILS['crystal_system']['tooltip']
    assert sg.getItemByPath(['space_group_name_HM_alt', 'tooltip']) == SG_DETAILS['space_group_name_HM_alt']['tooltip']
    assert sg.getItemByPath(['space_group_IT_number', 'tooltip']) == SG_DETAILS['space_group_IT_number']['tooltip']
    assert sg.getItemByPath(['origin_choice', 'tooltip']) == SG_DETAILS['origin_choice']['tooltip']

    assert sg.getItemByPath(['crystal_system', 'url']) == SG_DETAILS['crystal_system']['url']
    assert sg.getItemByPath(['space_group_name_HM_alt', 'url']) == SG_DETAILS['space_group_name_HM_alt']['url']
    assert sg.getItemByPath(['space_group_IT_number', 'url']) == SG_DETAILS['space_group_IT_number']['url']
    assert sg.getItemByPath(['origin_choice', 'url']) == SG_DETAILS['origin_choice']['url']

    return sg


def test_space_group_default():
    sg = genericTestSG(SpaceGroup.default)

    assert str(sg['crystal_system']['store']['unit']) == SG_DETAILS['crystal_system']['default'][1]
    assert sg['crystal_system'].value == SG_DETAILS['crystal_system']['default'][0]

    assert str(sg['space_group_name_HM_alt']['store']['unit']) == SG_DETAILS['space_group_name_HM_alt']['default'][1]
    assert sg['space_group_name_HM_alt'].value == SG_DETAILS['space_group_name_HM_alt']['default'][0]

    assert str(sg['space_group_IT_number']['store']['unit']) == SG_DETAILS['space_group_IT_number']['default'][1]
    assert sg['space_group_IT_number'].value == SG_DETAILS['space_group_IT_number']['default'][0]

    assert str(sg['origin_choice']['store']['unit']) == SG_DETAILS['origin_choice']['default'][1]
    assert sg['origin_choice'].value == SG_DETAILS['origin_choice']['default'][0]


def test_space_group_from_pars():
    crystal_system = 'aa'
    space_group_name_HM_alt = 'bb'
    space_group_IT_number = 101
    origin_choice = 'cc'

    sg = genericTestSG(SpaceGroup.fromPars, crystal_system, space_group_name_HM_alt, space_group_IT_number,
                       origin_choice)

    assert str(sg['crystal_system']['store']['unit']) == SG_DETAILS['crystal_system']['default'][1]
    assert sg['crystal_system'].value == crystal_system

    assert str(sg['space_group_name_HM_alt']['store']['unit']) == SG_DETAILS['space_group_name_HM_alt']['default'][1]
    assert sg['space_group_name_HM_alt'].value == space_group_name_HM_alt

    assert str(sg['space_group_IT_number']['store']['unit']) == SG_DETAILS['space_group_IT_number']['default'][1]
    assert sg['space_group_IT_number'].value == space_group_IT_number

    assert str(sg['origin_choice']['store']['unit']) == SG_DETAILS['origin_choice']['default'][1]
    assert sg['origin_choice'].value == origin_choice
