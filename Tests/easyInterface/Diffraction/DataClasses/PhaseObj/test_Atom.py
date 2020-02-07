import pytest
from easyInterface.Diffraction.DataClasses.PhaseObj.Atom import *
from Tests.easyInterface.Diffraction.DataClasses.Utils.Helpers import PathDictDerived


def genericTestAtom(atom_constructor, *args):
    expected = ['atom_site_label', 'type_symbol', 'scat_length_neutron', 'fract_x',
                'fract_y', 'fract_z', 'occupancy', 'adp_type', 'U_iso_or_equiv', 'ADP', 'MSP']

    expected_type = [str, Base, Base, Base, Base, Base, Base, Base, Base, (ADP, type(None)), (MSP, type(None))]
    PathDictDerived(atom_constructor, expected, expected_type, *args)

    atom = atom_constructor(*args)

    assert atom.getItemByPath(['type_symbol', 'header']) == ATOM_DETAILS['type_symbol']['header']
    assert atom.getItemByPath(['scat_length_neutron', 'header']) == ATOM_DETAILS['scat_length_neutron']['header']
    assert atom.getItemByPath(['fract_x', 'header']) == 'x'
    assert atom.getItemByPath(['fract_y', 'header']) == 'y'
    assert atom.getItemByPath(['fract_z', 'header']) == 'z'
    assert atom.getItemByPath(['occupancy', 'header']) == ATOM_DETAILS['occupancy']['header']
    assert atom.getItemByPath(['adp_type', 'header']) == ATOM_DETAILS['adp_type']['header']
    assert atom.getItemByPath(['U_iso_or_equiv', 'header']) == ATOM_DETAILS['U_iso_or_equiv']['header']

    assert atom.getItemByPath(['type_symbol', 'tooltip']) == ATOM_DETAILS['type_symbol']['tooltip']
    assert atom.getItemByPath(['scat_length_neutron', 'tooltip']) == ATOM_DETAILS['scat_length_neutron']['tooltip']
    assert atom.getItemByPath(['fract_x', 'tooltip']) == ATOM_DETAILS['fract']['tooltip']
    assert atom.getItemByPath(['fract_y', 'tooltip']) == ATOM_DETAILS['fract']['tooltip']
    assert atom.getItemByPath(['fract_z', 'tooltip']) == ATOM_DETAILS['fract']['tooltip']
    assert atom.getItemByPath(['occupancy', 'tooltip']) == ATOM_DETAILS['occupancy']['tooltip']
    assert atom.getItemByPath(['adp_type', 'tooltip']) == ATOM_DETAILS['adp_type']['tooltip']
    assert atom.getItemByPath(['U_iso_or_equiv', 'tooltip']) == ATOM_DETAILS['U_iso_or_equiv']['tooltip']

    assert atom.getItemByPath(['type_symbol', 'url']) == ATOM_DETAILS['type_symbol']['url']
    assert atom.getItemByPath(['scat_length_neutron', 'url']) == ATOM_DETAILS['scat_length_neutron']['url']
    assert atom.getItemByPath(['fract_x', 'url']) == ATOM_DETAILS['fract']['url']
    assert atom.getItemByPath(['fract_y', 'url']) == ATOM_DETAILS['fract']['url']
    assert atom.getItemByPath(['fract_z', 'url']) == ATOM_DETAILS['fract']['url']
    assert atom.getItemByPath(['occupancy', 'url']) == ATOM_DETAILS['occupancy']['url']
    assert atom.getItemByPath(['adp_type', 'url']) == ATOM_DETAILS['adp_type']['url']
    assert atom.getItemByPath(['U_iso_or_equiv', 'url']) == ATOM_DETAILS['U_iso_or_equiv']['url']

    return atom

def test_atom_default():
    site_label = 'Au1'
    atom = genericTestAtom(Atom.default, site_label)

    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == ATOM_DETAILS['type_symbol']['default'][0]
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['fract_x'].value == ATOM_DETAILS['fract']['default'][0]
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == ATOM_DETAILS['fract']['default'][0]
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == ATOM_DETAILS['fract']['default'][0]
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == ATOM_DETAILS['occupancy']['default'][0]
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == ATOM_DETAILS['adp_type']['default'][0]
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == ATOM_DETAILS['U_iso_or_equiv']['default'][0]
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atom_from_xyz():
    site_label = 'Au1'
    type_symbol = 'Au'
    pos = 0.1

    atom = genericTestAtom(Atom.fromXYZ, site_label, type_symbol, pos, pos, pos)

    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == type_symbol
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['fract_x'].value == pos
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == pos
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == pos
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == ATOM_DETAILS['occupancy']['default'][0]
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == ATOM_DETAILS['adp_type']['default'][0]
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == ATOM_DETAILS['U_iso_or_equiv']['default'][0]
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atom_from_parsNoADP_MSP():
    site_label = 'Au1'
    type_symbol = 'Au'
    scat_length_neutron = 0.15
    occupancy = 1.0
    adp_type = 'boo'
    U_iso_or_equiv = 2.0
    pos = 0.1

    atom = genericTestAtom(Atom.fromPars, site_label, type_symbol, scat_length_neutron, pos, pos, pos,
                    occupancy, adp_type, U_iso_or_equiv, None, None)


    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == type_symbol
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['scat_length_neutron'].value == scat_length_neutron
    assert str(atom['scat_length_neutron']['store']['unit']) == ATOM_DETAILS['scat_length_neutron']['default'][1]
    assert atom['fract_x'].value == pos
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == pos
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == pos
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == occupancy
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == adp_type
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == U_iso_or_equiv
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atom_from_parsNoMSP():
    site_label = 'Au1'
    type_symbol = 'Au'
    scat_length_neutron = 0.15
    occupancy = 1.0
    adp_type = 'boo'
    U_iso_or_equiv = 2.0
    pos = 0.1
    MSp = ['foo', *[0.275]*6]

    atom = genericTestAtom(Atom.fromPars, site_label, type_symbol, scat_length_neutron, pos, pos, pos,
                    occupancy, adp_type, U_iso_or_equiv, None, MSp)

    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == type_symbol
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['scat_length_neutron'].value == scat_length_neutron
    assert str(atom['scat_length_neutron']['store']['unit']) == ATOM_DETAILS['scat_length_neutron']['default'][1]
    assert atom['fract_x'].value == pos
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == pos
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == pos
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == occupancy
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == adp_type
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == U_iso_or_equiv
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atom_from_parsNoADP():
    site_label = 'Au1'
    type_symbol = 'Au'
    scat_length_neutron = 0.15
    occupancy = 1.0
    adp_type = 'boo'
    U_iso_or_equiv = 2.0
    pos = 0.1
    ADp = [0.175]*6

    atom = genericTestAtom(Atom.fromPars, site_label, type_symbol, scat_length_neutron, pos, pos, pos,
                    occupancy, adp_type, U_iso_or_equiv, ADp, None)

    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == type_symbol
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['scat_length_neutron'].value == scat_length_neutron
    assert str(atom['scat_length_neutron']['store']['unit']) == ATOM_DETAILS['scat_length_neutron']['default'][1]
    assert atom['fract_x'].value == pos
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == pos
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == pos
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == occupancy
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == adp_type
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == U_iso_or_equiv
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atom_from_pars():
    site_label = 'Au1'
    type_symbol = 'Au'
    scat_length_neutron = 0.15
    occupancy = 1.0
    adp_type = 'boo'
    U_iso_or_equiv = 2.0
    pos = 0.1
    ADp = [0.175]*6
    MSp = ['foo', *[0.275]*6]

    atom = genericTestAtom(Atom.fromPars, site_label, type_symbol, scat_length_neutron, pos, pos, pos,
                    occupancy, adp_type, U_iso_or_equiv, ADp, MSp)

    assert atom['atom_site_label'] == site_label
    assert atom['type_symbol'].value == type_symbol
    assert str(atom['type_symbol']['store']['unit']) == ATOM_DETAILS['type_symbol']['default'][1]
    assert atom['scat_length_neutron'].value == scat_length_neutron
    assert str(atom['scat_length_neutron']['store']['unit']) == ATOM_DETAILS['scat_length_neutron']['default'][1]
    assert atom['fract_x'].value == pos
    assert str(atom['fract_x']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_y'].value == pos
    assert str(atom['fract_y']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['fract_z'].value == pos
    assert str(atom['fract_z']['store']['unit']) == ATOM_DETAILS['fract']['default'][1]
    assert atom['occupancy'].value == occupancy
    assert str(atom['occupancy']['store']['unit']) == ATOM_DETAILS['occupancy']['default'][1]
    assert atom['adp_type'].value == adp_type
    assert str(atom['adp_type']['store']['unit']) == ATOM_DETAILS['adp_type']['default'][1]
    assert atom['U_iso_or_equiv'].value == U_iso_or_equiv
    assert str(atom['U_iso_or_equiv']['store']['unit']) == ATOM_DETAILS['U_iso_or_equiv']['default'][1]


def test_atoms():
    atoms = Atoms([])
    assert len(atoms) == 0
    atom = Atom.default('Ag')
    atoms[atom['atom_site_label']] = atom
    assert len(atoms) == 1
    atoms = Atoms([atom])
    assert len(atoms) == 1
    assert atom['atom_site_label'] in atoms.keys()
    atoms = Atoms(atom)
    assert len(atoms) == 1
    assert atom['atom_site_label'] in atoms.keys()


def genericTestADP(adp_constructor, *args):
    expected = ['u_11', 'u_22', 'u_33', 'u_12', 'u_13', 'u_23']

    expected_type = [Base, Base, Base, Base, Base, Base]
    PathDictDerived(adp_constructor, expected, expected_type, *args)

    adp = adp_constructor(*args)

    assert adp.getItemByPath(['u_11', 'header']) == 'U11'
    assert adp.getItemByPath(['u_22', 'header']) == 'U22'
    assert adp.getItemByPath(['u_33', 'header']) == 'U33'
    assert adp.getItemByPath(['u_12', 'header']) == 'U12'
    assert adp.getItemByPath(['u_13', 'header']) == 'U13'
    assert adp.getItemByPath(['u_23', 'header']) == 'U23'

    assert adp.getItemByPath(['u_11', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']
    assert adp.getItemByPath(['u_22', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']
    assert adp.getItemByPath(['u_33', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']
    assert adp.getItemByPath(['u_12', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']
    assert adp.getItemByPath(['u_13', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']
    assert adp.getItemByPath(['u_23', 'tooltip']) == ATOM_DETAILS['ADP']['tooltip']

    assert adp.getItemByPath(['u_11', 'url']) == ATOM_DETAILS['ADP']['url']
    assert adp.getItemByPath(['u_22', 'url']) == ATOM_DETAILS['ADP']['url']
    assert adp.getItemByPath(['u_33', 'url']) == ATOM_DETAILS['ADP']['url']
    assert adp.getItemByPath(['u_12', 'url']) == ATOM_DETAILS['ADP']['url']
    assert adp.getItemByPath(['u_13', 'url']) == ATOM_DETAILS['ADP']['url']
    assert adp.getItemByPath(['u_23', 'url']) == ATOM_DETAILS['ADP']['url']

    return adp

def test_ADP_default():
    adp = genericTestADP(ADP.default)

    assert str(adp['u_11']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_11'].value == ATOM_DETAILS['ADP']['default'][0]

    assert str(adp['u_22']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_22'].value == ATOM_DETAILS['ADP']['default'][0]

    assert str(adp['u_33']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_33'].value == ATOM_DETAILS['ADP']['default'][0]

    assert str(adp['u_12']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_12'].value == ATOM_DETAILS['ADP']['default'][0]

    assert str(adp['u_13']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_13'].value == ATOM_DETAILS['ADP']['default'][0]

    assert str(adp['u_23']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_23'].value == ATOM_DETAILS['ADP']['default'][0]


def test_ADP_from_pars():

    u = 0.15

    adp = genericTestADP(ADP.fromPars, u, u, u, u, u, u)

    assert str(adp['u_11']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_11'].value == u

    assert str(adp['u_22']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_22'].value == u

    assert str(adp['u_33']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_33'].value == u

    assert str(adp['u_12']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_12'].value == u

    assert str(adp['u_13']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_13'].value == u

    assert str(adp['u_23']['store']['unit']) == ATOM_DETAILS['ADP']['default'][1]
    assert adp['u_23'].value == u


def test_ADP_is_empty():
    adp = ADP.default()
    assert adp.isEmpty()
    u = 0.15
    adp = ADP.fromPars(u, u, u, u, u, u)
    assert not adp.isEmpty()


def genericTestMSP(msp_constructor, *args):
    expected = ['type', 'chi_11', 'chi_22', 'chi_33', 'chi_12', 'chi_13', 'chi_23']

    expected_type = [Base, Base, Base, Base, Base, Base, Base]
    PathDictDerived(msp_constructor, expected, expected_type, *args)

    msp = msp_constructor(*args)

    assert msp.getItemByPath(['type', 'header']) == 'Type'
    assert msp.getItemByPath(['chi_11', 'header']) == 'U11'
    assert msp.getItemByPath(['chi_22', 'header']) == 'U22'
    assert msp.getItemByPath(['chi_33', 'header']) == 'U33'
    assert msp.getItemByPath(['chi_12', 'header']) == 'U12'
    assert msp.getItemByPath(['chi_13', 'header']) == 'U13'
    assert msp.getItemByPath(['chi_23', 'header']) == 'U23'

    assert msp.getItemByPath(['type', 'tooltip']) == ''
    assert msp.getItemByPath(['chi_11', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']
    assert msp.getItemByPath(['chi_22', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']
    assert msp.getItemByPath(['chi_33', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']
    assert msp.getItemByPath(['chi_12', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']
    assert msp.getItemByPath(['chi_13', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']
    assert msp.getItemByPath(['chi_23', 'tooltip']) == ATOM_DETAILS['MSP']['tooltip']

    assert msp.getItemByPath(['type', 'url']) == ''
    assert msp.getItemByPath(['chi_11', 'url']) == ATOM_DETAILS['MSP']['url']
    assert msp.getItemByPath(['chi_22', 'url']) == ATOM_DETAILS['MSP']['url']
    assert msp.getItemByPath(['chi_33', 'url']) == ATOM_DETAILS['MSP']['url']
    assert msp.getItemByPath(['chi_12', 'url']) == ATOM_DETAILS['MSP']['url']
    assert msp.getItemByPath(['chi_13', 'url']) == ATOM_DETAILS['MSP']['url']
    assert msp.getItemByPath(['chi_23', 'url']) == ATOM_DETAILS['MSP']['url']

    return msp

def test_MSP_default():
    msp = genericTestMSP(MSP.default)

    assert str(msp['type']['store']['unit']) == ''
    assert msp['type'].value is None

    assert str(msp['chi_11']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_11'].value == ATOM_DETAILS['MSP']['default'][0]

    assert str(msp['chi_22']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_22'].value == ATOM_DETAILS['MSP']['default'][0]

    assert str(msp['chi_33']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_33'].value == ATOM_DETAILS['MSP']['default'][0]

    assert str(msp['chi_12']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_12'].value == ATOM_DETAILS['MSP']['default'][0]

    assert str(msp['chi_13']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_13'].value == ATOM_DETAILS['MSP']['default'][0]

    assert str(msp['chi_23']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_23'].value == ATOM_DETAILS['MSP']['default'][0]


def test_MSP_from_pars():

    msp_type = 'a'
    u = 0.15

    msp = genericTestMSP(MSP.fromPars, msp_type, u, u, u, u, u, u)

    assert str(msp['type']['store']['unit']) == ''
    assert msp['type'].value == msp_type

    assert str(msp['chi_11']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_11'].value == u

    assert str(msp['chi_22']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_22'].value == u

    assert str(msp['chi_33']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_33'].value == u

    assert str(msp['chi_12']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_12'].value == u

    assert str(msp['chi_13']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_13'].value == u

    assert str(msp['chi_23']['store']['unit']) == ATOM_DETAILS['MSP']['default'][1]
    assert msp['chi_23'].value == u


def test_MSP_is_empty():
    msp = MSP.default()
    assert msp.isEmpty()
    u = 0.15
    msp_type = 'a'
    msp = MSP.fromPars(msp_type, u, u, u, u, u, u)
    assert not msp.isEmpty()
