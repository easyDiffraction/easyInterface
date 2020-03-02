from easyInterface.Common.PhaseObj.Cell import *
from tests.easyInterface.Common.Utils.Helpers import PathDictDerived


def genericTestCell(cell_constructor, *args):
    expected = ['length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma']

    expected_type = [Base, Base, Base, Base, Base, Base]
    PathDictDerived(cell_constructor, expected, expected_type, *args)

    cell = cell_constructor(*args)

    assert cell.getItemByPath(['length_a', 'header']) == 'a (Å)'
    assert cell.getItemByPath(['length_b', 'header']) == 'b (Å)'
    assert cell.getItemByPath(['length_c', 'header']) == 'c (Å)'
    assert cell.getItemByPath(['angle_alpha', 'header']) == 'alpha (°)'
    assert cell.getItemByPath(['angle_beta', 'header']) == 'beta (°)'
    assert cell.getItemByPath(['angle_gamma', 'header']) == 'gamma (°)'

    assert cell.getItemByPath(['length_a', 'tooltip']) == CELL_DETAILS['length']['tooltip']
    assert cell.getItemByPath(['length_b', 'tooltip']) == CELL_DETAILS['length']['tooltip']
    assert cell.getItemByPath(['length_c', 'tooltip']) == CELL_DETAILS['length']['tooltip']
    assert cell.getItemByPath(['angle_alpha', 'tooltip']) == CELL_DETAILS['angle']['tooltip']
    assert cell.getItemByPath(['angle_beta', 'tooltip']) == CELL_DETAILS['angle']['tooltip']
    assert cell.getItemByPath(['angle_gamma', 'tooltip']) == CELL_DETAILS['angle']['tooltip']

    assert cell.getItemByPath(['length_a', 'url']) == CELL_DETAILS['length']['url']
    assert cell.getItemByPath(['length_b', 'url']) == CELL_DETAILS['length']['url']
    assert cell.getItemByPath(['length_c', 'url']) == CELL_DETAILS['length']['url']
    assert cell.getItemByPath(['angle_alpha', 'url']) == CELL_DETAILS['angle']['url']
    assert cell.getItemByPath(['angle_beta', 'url']) == CELL_DETAILS['angle']['url']
    assert cell.getItemByPath(['angle_gamma', 'url']) == CELL_DETAILS['angle']['url']

    return cell


def test_cell_default():
    cell = genericTestCell(Cell.default)

    assert str(cell['length_a']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_a'].value == CELL_DETAILS['length']['default'][0]

    assert str(cell['length_b']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_b'].value == CELL_DETAILS['length']['default'][0]

    assert str(cell['length_c']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_c'].value == CELL_DETAILS['length']['default'][0]

    assert str(cell['angle_alpha']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_alpha'].value == CELL_DETAILS['angle']['default'][0]

    assert str(cell['angle_beta']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_beta'].value == CELL_DETAILS['angle']['default'][0]

    assert str(cell['angle_gamma']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_gamma'].value == CELL_DETAILS['angle']['default'][0]


def test_cell_from_pars():
    length = 5
    angle = 60

    cell = genericTestCell(Cell.fromPars, length, length, length, angle, angle, angle)

    assert str(cell['length_a']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_a'].value == length

    assert str(cell['length_b']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_b'].value == length

    assert str(cell['length_c']['store']['unit']) == CELL_DETAILS['length']['default'][1]
    assert cell['length_c'].value == length

    assert str(cell['angle_alpha']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_alpha'].value == angle

    assert str(cell['angle_beta']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_beta'].value == angle

    assert str(cell['angle_gamma']['store']['unit']) == CELL_DETAILS['angle']['default'][1]
    assert cell['angle_gamma'].value == angle