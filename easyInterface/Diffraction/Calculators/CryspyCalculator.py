import os

from typing import Tuple

import cryspy
import pycifstar

from asteval import Interpreter

from easyInterface.Diffraction.DataClasses.DataObj.Calculation import *
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import *
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import *
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import Base

from easyInterface.Utils.Helpers import time_it

# Imports needed to create a cryspyObj
from cryspy.scripts.cl_rhochi import RhoChi
from cryspy.cif_like.cl_crystal import Crystal
from cryspy.cif_like.cl_pd import Phase as cpPhase
from cryspy.cif_like.cl_pd import Pd, PdBackground, PdBackgroundL, PdInstrResolution, PdMeas, PdMeasL, PhaseL, Setup

# Imports needed to create a phase
from cryspy.corecif.cl_cell import Cell as cpCell
from cryspy.corecif.cl_atom_site import AtomSite, AtomSiteL
from cryspy.corecif.cl_atom_site_aniso import AtomSiteAniso, AtomSiteAnisoL
from cryspy.magneticcif.cl_atom_site_susceptibility import AtomSiteSusceptibility, AtomSiteSusceptibilityL
from cryspy.symcif.cl_space_group import SpaceGroup as cpSpaceGroup

from easyInterface import logger as logging

PHASE_SEGMENT = "_phases"
EXPERIMENT_SEGMENT = "_experiments"

CALCULATOR_INFO = {
    'name': 'CrysPy',
    'version': '0.2.0',
    'url': 'https://github.com/ikibalin/cryspy'
}


class CryspyCalculator:
    def __init__(self, main_rcif_path: Union[str, type(None)] = None):
        self._log = logging.getLogger(__class__.__module__)
        self._experiment_name = []
        self._main_rcif_path = main_rcif_path
        self._main_rcif = None
        self._phases_path = ""
        self._phase_name = []
        self._experiments_path = ""
        self._cryspy_obj = self._createCryspyObj()
        self._log.info('Created cryspy calculator interface')

    @staticmethod
    def calculatorInfo() -> dict:
        return CALCULATOR_INFO

    @time_it
    def _createCryspyObj(self):
        """
        Create cryspy object from separate rcif files
        """

        self._log.debug('----> Start')
        self._log.info('Creating cryspy object')
        try:
            phase_segment = self._parseSegment(PHASE_SEGMENT)
        except TypeError:
            self._log.warning('Main cif location is not a path')
            return RhoChi()
        full_rcif_content = self._parseSegment(EXPERIMENT_SEGMENT) + phase_segment
        # update the phase name global
        self._log.debug('Calling RhoChi')
        rho_chi = RhoChi().from_cif(full_rcif_content)
        if rho_chi is None:
            self._log.debug('Main CIF is empty')
            rho_chi = RhoChi()
        else:
            self._log.debug('Populating _phase_name with cryspy phase names')
            self._phase_name = [phase.data_name for phase in rho_chi.crystals]
            self._experiment_name = [experiment.data_name for experiment in rho_chi.experiments]
        self._log.debug('<---- End')
        return rho_chi

    def _parseSegment(self, segment: str = "") -> str:
        """
        Parse the given segment info from the main rcif file
        :param segment:
        :return: Parsed cif file content
        """
        self._log.debug('----> Start')
        self._log.info('Reading main cif file')
        if not segment:
            self._log.debug('segment is empty')
            return ""
        if segment not in (PHASE_SEGMENT, EXPERIMENT_SEGMENT):
            self._log.debug('segment not in phase or experiment')
            return ""
        rcif_dir_name = os.path.dirname(self._main_rcif_path)
        try:
            self._main_rcif = pycifstar.read_star_file(self._main_rcif_path)
        except FileNotFoundError:
            self._log.warning('Main cif can not be found')
        rcif_content = ""
        if segment in str(self._main_rcif):
            self._log.debug('segment in main cif')
            segment_rcif_path = os.path.join(rcif_dir_name, self._main_rcif[segment].value)
            if os.path.isfile(segment_rcif_path):
                with open(segment_rcif_path, 'r') as f:
                    self._log.debug('Reading cif segment')
                    segment_rcif_content = f.read()
                    rcif_content += segment_rcif_content
        self._log.debug('<---- End')
        return rcif_content

    def setExpsDefinition(self, exp_path: str):
        self._log.debug('----> Start')
        """
        Set cryspy.experiments from a single file. *Removes all others*
        """
        rcif_content = ""
        if not isinstance(exp_path, (str, os.PathLike)):
            self._log.warning('Experiment definition is not a string or path')
            return

        # This will read the CIF file
        if os.path.isfile(exp_path):
            with open(exp_path, 'r') as f:
                self._log.debug('Reading experiment cif file')
                exp_rcif_content = f.read()
                rcif_content += exp_rcif_content
            self._experiments_path = exp_path
        else:
            self._log.warning('Experiment cif can not be found')
            return

        experiment = Pd.from_cif(exp_rcif_content)
        self._cryspy_obj.experiments = [experiment]
        self._experiment_name = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        self._log.info('Setting cryspy experiments from cif content')
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.experiments[0].phase.items[0] = (self._phase_name[0])
        self._log.debug('<---- End')

    def addExpsDefinition(self, exp_path: str):
        self._log.debug('----> Start')
        """
        Add an experiment to cryspy.experiments
        """
        if not isinstance(exp_path, (str, os.PathLike)):
            self._log.warning('Experiment definition is not a string or path')
            return

        exp_rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(exp_path):
            with open(exp_path, 'r') as f:
                self._log.debug('Reading cif content for experiment definition')
                exp_rcif_content = f.read()
            self._experiments_path = exp_path
        else:
            self._log.warning('Experiment cif can not be found')

        experiment = Pd.from_cif(exp_rcif_content)
        if self._cryspy_obj.experiments is not None:
            self._log.info('Adding experiment to cryspy experiments')
            self._cryspy_obj.experiments = [*self._cryspy_obj.experiments, experiment]
        else:
            self._log.info('Experiment set from cif content')
            self._cryspy_obj.experiments = [experiment]
            if self._cryspy_obj.crystals is not None:
                self._log.debug('Setting Experiment to be the pattern for the first phase')
                self._cryspy_obj.experiments[0].phase.items[0] = (self._phase_name[0])
        self._experiment_name = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        self._log.debug('<---- End')

    def removeExpsDefinition(self, name: str):
        self._log.debug('----> Start')
        if name in self._experiment_name:
            self._log.info('Experiment found, removing')
            experiments = self._cryspy_obj.experiments
            self._cryspy_obj.experiments = [experiment for experiment in experiments if experiment.data_name != name]
            self._experiment_name = []
            if self._cryspy_obj.experiments:
                self._experiment_name = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        else:
            raise KeyError
        self._log.debug('<---- End')

    def setPhaseDefinition(self, phases_path: str):
        self._log.debug('----> Start')

        """
        Parse the relevant phases file and update the corresponding model
        """
        rcif_content = ""
        if not isinstance(phases_path, (str, os.PathLike)):
            self._log.warning('Phase definition is not a string or path')
            return

        # This will read the CIF file
        if os.path.isfile(phases_path):
            with open(phases_path, 'r') as f:
                phases_rcif_content = f.read()
                rcif_content += phases_rcif_content
            self._phases_path = phases_path
        else:
            self._log.warning('Phase cif can not be found')
            return

        # find the name of the new phase
        self._log.info('Setting phase to cryspy crystals')
        phase = Crystal().from_cif(phases_rcif_content)
        new_phase_name = phase.data_name
        self._cryspy_obj.crystals = [phase]
        self._phase_name = [phase.data_name for phase in self._cryspy_obj.crystals]

        experiment_segment = ''
        if self._cryspy_obj.experiments is not None:
            if isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) and len(self._cryspy_obj.experiments) > 0:
                if len(self._cryspy_obj.experiments[0].phase.items) > 0:
                    pass
                # TODO note only the first exp
                experiment_segment = self._cryspy_obj.experiments[0].to_cif()
                # Concatenate the corrected experiment and the new CIF
                rcif_content = rcif_content + "\n" + experiment_segment
                # This will update the CrysPy object
                self._cryspy_obj.from_cif(rcif_content)
                #
                self._log.info('Setting phase to existing experiment')
                self.associatePhaseToExp(self._cryspy_obj.experiments[0].data_name, new_phase_name, 0.0)
                # self._cryspy_obj.experiments[0].phase.items[0] = (new_phase_name)
        self._log.debug('<---- End')

    def addPhaseDefinition(self, phases_path: str):
        self._log.debug('----> Start')
        """
        Parse the relevant phases file and update the corresponding model
        """
        if not isinstance(phases_path, (str, os.PathLike)):
            self._log.warning('Phase definition is not a string or path')
            return

        phases_rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(phases_path):
            with open(phases_path, 'r') as f:
                phases_rcif_content = f.read()
            self._phases_path = phases_path
        else:
            self._log.warning('Phase cif can not be found')
            return

        # find the name of the new phase
        phase = Crystal().from_cif(phases_rcif_content)
        if self._cryspy_obj.crystals is not None:
            self._log.info('Adding phase to existing phases')
            self._cryspy_obj.crystals = [*self._cryspy_obj.crystals, phase]
        else:
            self._log.info('Setting cryspy crystal to phase')
            self._cryspy_obj.crystals = [phase]
        self._phase_name = [phase.data_name for phase in self._cryspy_obj.crystals]
        self._log.debug('<---- End')

    def removePhaseDefinition(self, name: str):
        self._log.debug('----> Start')
        if name in self._phase_name:
            crystals = self._cryspy_obj.crystals
            self._cryspy_obj.crystals = [crystal for crystal in crystals if crystal.data_name != name]
            self._phase_name = []
            if self._cryspy_obj.crystals:
                self._phase_name = [phase.data_name for phase in self._cryspy_obj.crystals]
            self._log.info('Removing phase %s', name)
        else:
            self._log.warning('Phase not found in cryspy crystals')
            raise KeyError
        # See if this is associated to an experiment....
        for experiment in self._cryspy_obj.experiments:
            if name in self.getPhasesAssocatedToExp(experiment.data_name):
                self.disassociatePhaseToExp(experiment.data_name, name)
        self._log.debug('<---- End')

    def writeMainCif(self, save_dir: str, filename: str = 'main.cif', exp_name: str = 'experiments.cif',
                     phase_name: str = 'phases.cif'):
        self._log.debug('----> Start')
        self._log.info('Writing main cif file')
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        main_block = self._main_rcif
        save_to = os.path.join(save_dir, filename)
        if self._cryspy_obj.crystals is not None:
            main_block["_phases"].value = phase_name
        if self._cryspy_obj.experiments is not None:
            main_block["_experiments"].value = exp_name
        try:
            main_block.to_file(save_to)
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def writePhaseCif(self, save_dir: str, phase_name: str = 'phases.cif'):
        self._log.debug('----> Start')
        save_to = os.path.join(save_dir, phase_name)
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        phases_block = pycifstar.Global()
        if self._cryspy_obj.crystals is not None:
            self._log.info('Writing phase cif files')
            phase_str = ''
            for crystal in self._cryspy_obj.crystals:
                phase_str + crystal.to_cif() + '\n'
            phases_block.take_from_string(phase_str)
        else:
            self._log.info('No experiments to save. creating empty file: %s', save_to)
        try:
            phases_block.to_file(save_to)
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def writeExpCif(self, save_dir: str, exp_name: str = 'experiments.cif'):
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        save_to = os.path.join(save_dir, exp_name)
        exp_block = pycifstar.Global()
        if self._cryspy_obj.experiments is not None:
            exp_str = ''
            for experiment in self._cryspy_obj.experiments:
                exp_str + experiment.to_cif() + '\n'
            exp_block.take_from_string(exp_str)
        else:
            self._log.info('No experiments to save. creating empty file: %s', save_to)
        try:
            exp_block.to_file(save_to)
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def saveCifs(self, save_dir: str, filename: str = 'main.cif', exp_name: str = 'experiments.cif',
                 phase_name: str = 'phases.cif'):
        self._log.debug('----> Start')
        try:
            self.writeMainCif(save_dir, filename)
            self.writePhaseCif(save_dir, phase_name)
            self.writeExpCif(save_dir, exp_name)
            self._log.info('Cifs saved successfully')
        except PermissionError:
            self._log.warning('Unable to save cifs')
        self._log.debug('<---- End')

    @staticmethod
    def _createProjItemFromObj(func, keys: list, obj_list: list):
        """ ... """
        ret_vals = func(
            *[item.value if isinstance(item, cryspy.common.cl_fitable.Fitable) else item for item in obj_list])
        for index, key in enumerate(keys):
            if not isinstance(obj_list[index], cryspy.common.cl_fitable.Fitable):
                continue
            elif isinstance(ret_vals[key], Base):
                ret_vals.setItemByPath([key, 'store', 'error'], obj_list[index].sigma)
                ret_vals.setItemByPath([key, 'store', 'constraint'], obj_list[index].constraint)
                ret_vals.setItemByPath([key, 'store', 'hide'], obj_list[index].constraint_flag)
                ret_vals.setItemByPath([key, 'store', 'refine'], obj_list[index].refinement)
        return ret_vals

    @time_it
    def getPhases(self) -> Phases:
        """Set phases (sample model tab in GUI)"""

        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) or self._cryspy_obj.crystals is None:
            return Phases({})

        self._cryspy_obj.apply_constraint()  # THIS IS 400ms !!!!!!
        phases = list(map(self._makePhase, self._cryspy_obj.crystals))
        phases = Phases(phases)
        self._log.info(phases)
        return phases

    def readPhaseDefinition(self, phases_path):
        self._log.debug('----> Start')

        """
        Parse the relevant phases file and update the corresponding model
        """
        phases_rcif_content = ""
        if not isinstance(phases_path, (str, os.PathLike)):
            self._log.warning('Phase definition is not a string or path')
            return

        # This will read the CIF file
        if os.path.isfile(phases_path):
            with open(phases_path, 'r') as f:
                phases_rcif_content = f.read()
        phase_cp = cpPhase().from_cif(phases_rcif_content)
        phase = self._makePhase(phase_cp)
        self._log.debug('<---- End')
        return phase, phase_cp

    def _makePhase(self, calculator_phase: Crystal):
        # This is ~180ms per atom in phase. Limited by cryspy 
        calculator_phase_name = calculator_phase.data_name
        # This group is < 1ms
        space_group = self._getPhasesSpace_group(calculator_phase_name)
        unit_cell = self._getPhaseCell(calculator_phase_name)
        phase = Phase.fromPars(calculator_phase_name, space_group, unit_cell)
        # Atom sites ~ 6ms
        atoms = list(map(lambda x: self._makeAtom(calculator_phase, x), calculator_phase.atom_site.label))
        atoms = Atoms(atoms)
        
        for key in atoms:
            phase['atoms'][key] = atoms[key]

        # This is ~125ms per atom due to cryspy taking ~110ms :-(
        self._makeAtomSites(phase, calculator_phase)
        return phase

    def _makeAtom(self, calculator_phase: Crystal, label: str):
        # This is ~2ms
        i = calculator_phase.atom_site.label.index(label)
        calculator_atom_site = calculator_phase.atom_site
        if self._cryspy_obj.crystals is not None:
            try:
                ii = self._cryspy_obj.crystals.index(calculator_phase)
            except ValueError:
                # Phase has not been added to crystal. Assume that it will be, possibly in error :-/
                ii = len(self._cryspy_obj.crystals)
        else:
            # There are no crystals yet. assume that it will be added.
            ii = 0  
        mapping_base = 'self._cryspy_obj.crystals'
        mapping_phase = mapping_base + '[{}]'.format(ii)
        mapping_atom = mapping_phase + '.atom_site'

        # Atom sites symbol
        type_symbol = calculator_atom_site.type_symbol[i]

        # Atom site neutron scattering length
        scat_length_neutron = calculator_atom_site.scat_length_neutron[i]

        # Atom site coordinates
        fract_x = calculator_atom_site.fract_x[i]
        fract_y = calculator_atom_site.fract_y[i]
        fract_z = calculator_atom_site.fract_z[i]

        # Atom site occupancy
        occupancy = calculator_atom_site.occupancy[i]

        # Atom site ADP type
        adp_type = calculator_atom_site.adp_type[i]

        # Atom site isotropic ADP
        U_iso_or_equiv = calculator_atom_site.u_iso_or_equiv[i]

        # Atom site anisotropic ADP
        adp = None
        if calculator_phase.atom_site_aniso is not None:
            if i < len(calculator_phase.atom_site_aniso.u_11):
                mapping_adp = mapping_phase + '.atom_site_aniso'

                adp = [calculator_phase.atom_site_aniso.u_11[i],
                       calculator_phase.atom_site_aniso.u_22[i],
                       calculator_phase.atom_site_aniso.u_33[i],
                       calculator_phase.atom_site_aniso.u_12[i],
                       calculator_phase.atom_site_aniso.u_13[i],
                       calculator_phase.atom_site_aniso.u_23[i]]
                adp = self._createProjItemFromObj(ADP.fromPars,
                                                  ['u_11', 'u_22', 'u_33',
                                                   'u_12', 'u_13', 'u_23'],
                                                  adp)
                adp['u_11']['mapping'] = mapping_adp + '.u_11[{}]'.format(i)
                adp['u_22']['mapping'] = mapping_adp + '.u_22[{}]'.format(i)
                adp['u_33']['mapping'] = mapping_adp + '.u_33[{}]'.format(i)
                adp['u_12']['mapping'] = mapping_adp + '.u_12[{}]'.format(i)
                adp['u_13']['mapping'] = mapping_adp + '.u_13[{}]'.format(i)
                adp['u_23']['mapping'] = mapping_adp + '.u_23[{}]'.format(i)

        # Atom site MSP
        msp = None
        if calculator_phase.atom_site_susceptibility is not None:
            if i < len(calculator_phase.atom_site_susceptibility.chi_type):
                mapping_msp = mapping_phase + '.atom_site_susceptibility'

                msp = [calculator_phase.atom_site_susceptibility.chi_type[i],
                       calculator_phase.atom_site_susceptibility.chi_11[i],
                       calculator_phase.atom_site_susceptibility.chi_22[i],
                       calculator_phase.atom_site_susceptibility.chi_33[i],
                       calculator_phase.atom_site_susceptibility.chi_12[i],
                       calculator_phase.atom_site_susceptibility.chi_13[i],
                       calculator_phase.atom_site_susceptibility.chi_23[i]]
                msp = self._createProjItemFromObj(MSP.fromPars,
                                                  ['MSPtype', 'chi_11', 'chi_22', 'chi_33',
                                                   'chi_12', 'chi_13', 'chi_23'],
                                                  msp)
                msp['type']['mapping'] = mapping_msp + '.chi_type[{}]'.format(i)
                msp['chi_11']['mapping'] = mapping_msp + '.chi_11[{}]'.format(i)
                msp['chi_22']['mapping'] = mapping_msp + '.chi_22[{}]'.format(i)
                msp['chi_33']['mapping'] = mapping_msp + '.chi_33[{}]'.format(i)
                msp['chi_12']['mapping'] = mapping_msp + '.chi_12[{}]'.format(i)
                msp['chi_13']['mapping'] = mapping_msp + '.chi_13[{}]'.format(i)
                msp['chi_23']['mapping'] = mapping_msp + '.chi_23[{}]'.format(i)

        # Add an atom to atoms
        atom = self._createProjItemFromObj(
            Atom.fromPars,
            ['atom_site_label', 'type_symbol', 'scat_length_neutron',
             'fract_x', 'fract_y', 'fract_z', 'occupancy', 'adp_type',
             'U_iso_or_equiv'],
            [label, type_symbol, scat_length_neutron,
             fract_x, fract_y, fract_z, occupancy, adp_type,
             U_iso_or_equiv, adp, msp])

        atom['scat_length_neutron']['mapping'] = mapping_atom + '.scat_length_neutron[{}]'.format(i)
        atom['fract_x']['mapping'] = mapping_atom + '.fract_x[{}]'.format(i)
        atom['fract_y']['mapping'] = mapping_atom + '.fract_y[{}]'.format(i)
        atom['fract_z']['mapping'] = mapping_atom + '.fract_z[{}]'.format(i)
        atom['occupancy']['mapping'] = mapping_atom + '.occupancy[{}]'.format(i)
        atom['adp_type']['mapping'] = mapping_atom + '.adp_type[{}]'.format(i)
        atom['U_iso_or_equiv']['mapping'] = mapping_atom + '.u_iso_or_equiv[{}]'.format(i)
        return atom

    @staticmethod
    def _makeAtomSites(phase: Phase, calculator_phase: Crystal):
        atom_site_list = [[], [], [], []]
        # Atom sites for structure view (all the positions inside unit cell of 1x1x1)
        for x, y, z, scat_length_neutron in zip(calculator_phase.atom_site.fract_x,
                                                calculator_phase.atom_site.fract_y,
                                                calculator_phase.atom_site.fract_z,
                                                calculator_phase.atom_site.scat_length_neutron):
            x_array, y_array, z_array, _ = calculator_phase.space_group.calc_xyz_mult(x.value, y.value, z.value)
            scat_length_neutron_array = np.full_like(x_array, scat_length_neutron)
            atom_site_list[0] += x_array.tolist()
            atom_site_list[1] += y_array.tolist()
            atom_site_list[2] += z_array.tolist()
            atom_site_list[3] += scat_length_neutron_array.tolist()
        for x, y, z, scat_length_neutron in zip(atom_site_list[0], atom_site_list[1], atom_site_list[2],
                                                atom_site_list[3]):
            if x == 0.0:
                atom_site_list[0].append(1.0)
                atom_site_list[1].append(y)
                atom_site_list[2].append(z)
                atom_site_list[3].append(scat_length_neutron)
            if y == 0.0:
                atom_site_list[0].append(x)
                atom_site_list[1].append(1.0)
                atom_site_list[2].append(z)
                atom_site_list[3].append(scat_length_neutron)
            if z == 0.0:
                atom_site_list[0].append(x)
                atom_site_list[1].append(y)
                atom_site_list[2].append(1.0)
                atom_site_list[3].append(scat_length_neutron)

        phase.setItemByPath(['sites', 'fract_x'], atom_site_list[0])
        phase.setItemByPath(['sites', 'fract_y'], atom_site_list[1])
        phase.setItemByPath(['sites', 'fract_z'], atom_site_list[2])
        phase.setItemByPath(['sites', 'scat_length_neutron'], atom_site_list[3])

    def _getPhasesSpace_group(self, phase_name: str) -> SpaceGroup:
        mapping_base = 'self._cryspy_obj.crystals'
        i = self._phase_name.index(phase_name)
        calculator_phase = self._cryspy_obj.crystals[i]
        # logging.info(calculator_phase_name)
        mapping_phase = mapping_base + '[{}]'.format(i)
        # Space group
        space_group = self._createProjItemFromObj(SpaceGroup.fromPars,
                                                  ['crystal_system', 'space_group_name_HM_alt',
                                                   'space_group_IT_number', 'origin_choice'],
                                                  [calculator_phase.space_group.crystal_system,
                                                   calculator_phase.space_group.name_hm_ref,
                                                   calculator_phase.space_group.it_number,
                                                   calculator_phase.space_group.it_coordinate_system_code])

        space_group['crystal_system']['mapping'] = mapping_phase + '.space_group.crystal_system'
        space_group['space_group_name_HM_alt']['mapping'] = mapping_phase + '.space_group.name_hm_ref'
        space_group['space_group_IT_number']['mapping'] = mapping_phase + '.space_group.it_number'
        space_group['origin_choice']['mapping'] = mapping_phase + '.space_group.it_coordinate_system_code'
        return space_group

    def _getPhaseCell(self, phase_name:str) -> Cell:
        mapping_base = 'self._cryspy_obj.crystals'
        i = self._phase_name.index(phase_name)
        calculator_phase = self._cryspy_obj.crystals[i]
        # logging.info(calculator_phase_name)
        mapping_phase = mapping_base + '[{}]'.format(i)
        unit_cell = self._createProjItemFromObj(Cell.fromPars, ['length_a', 'length_b', 'length_c',
                                                                'angle_alpha', 'angle_beta', 'angle_gamma'],
                                                [calculator_phase.cell.length_a, calculator_phase.cell.length_b,
                                                 calculator_phase.cell.length_c, calculator_phase.cell.angle_alpha,
                                                 calculator_phase.cell.angle_beta,
                                                 calculator_phase.cell.angle_gamma])

        unit_cell['length_a']['mapping'] = mapping_phase + '.cell.length_a'
        unit_cell['length_b']['mapping'] = mapping_phase + '.cell.length_b'
        unit_cell['length_c']['mapping'] = mapping_phase + '.cell.length_c'
        unit_cell['angle_alpha']['mapping'] = mapping_phase + '.cell.angle_alpha'
        unit_cell['angle_beta']['mapping'] = mapping_phase + '.cell.angle_beta'
        unit_cell['angle_gamma']['mapping'] = mapping_phase + '.cell.angle_gamma'
        return unit_cell

    @time_it
    def getExperiments(self) -> Experiments:
        experiments = []

        mapping_base = 'self._cryspy_obj.experiments'

        if self._cryspy_obj.experiments is None:
            return Experiments({})

        for i, calculator_experiment in enumerate(self._cryspy_obj.experiments):
            calculator_experiment_name = calculator_experiment.data_name

            mapping_exp = mapping_base + '[{}]'.format(i)

            # Experimental setup
            calculator_setup = calculator_experiment.setup
            wavelength = calculator_setup.wavelength
            offset = calculator_setup.offset_ttheta

            # Scale
            scale = calculator_experiment.phase.scale

            # Background
            calculator_background = calculator_experiment.background
            backgrounds = []
            for ii, (ttheta, intensity) in enumerate(
                    zip(calculator_background.ttheta, calculator_background.intensity)):
                background = self._createProjItemFromObj(Background.fromPars, ['ttheta', 'intensity'],
                                                         [ttheta, intensity])
                background['intensity']['mapping'] = mapping_exp + '.background.intensity[{}]'.format(ii)
                backgrounds.append(background)
            backgrounds = Backgrounds(backgrounds)

            # Instrument resolution
            calculator_resolution = calculator_experiment.resolution
            resolution = self._createProjItemFromObj(Resolution.fromPars,
                                                     ['u', 'v', 'w', 'x', 'y'],
                                                     [calculator_resolution.u,
                                                      calculator_resolution.v,
                                                      calculator_resolution.w,
                                                      calculator_resolution.x,
                                                      calculator_resolution.y])
            resolution['u']['mapping'] = mapping_exp + '.resolution.u'
            resolution['v']['mapping'] = mapping_exp + '.resolution.v'
            resolution['w']['mapping'] = mapping_exp + '.resolution.w'
            resolution['x']['mapping'] = mapping_exp + '.resolution.x'
            resolution['y']['mapping'] = mapping_exp + '.resolution.y'

            # Measured data points
            x_obs = np.array(calculator_experiment.meas.ttheta).tolist()
            y_obs_up = None
            sy_obs_up = None
            y_obs_down = None
            sy_obs_down = None
            y_obs = None
            sy_obs = None
            if calculator_experiment.meas.intensity[0] is not None:
                y_obs = np.array(calculator_experiment.meas.intensity).tolist()
                sy_obs = np.array(calculator_experiment.meas.intensity_sigma).tolist()
            elif calculator_experiment.meas.intensity_up[0] is not None:
                y_obs_up = np.array(calculator_experiment.meas.intensity_up)
                sy_obs_up = np.array(calculator_experiment.meas.intensity_up_sigma).tolist()
                y_obs_down = np.array(calculator_experiment.meas.intensity_down)
                sy_obs_down = np.array(calculator_experiment.meas.intensity_down_sigma).tolist()
                y_obs = (y_obs_up + y_obs_down).tolist()
                y_obs_up = y_obs_up.tolist()
                y_obs_down = y_obs_down.tolist()
                sy_obs = np.sqrt(np.square(sy_obs_up) + np.square(sy_obs_down)).tolist()

            data = MeasuredPattern(x_obs, y_obs, sy_obs, y_obs_up, sy_obs_up, y_obs_down, sy_obs_down)

            experiment = self._createProjItemFromObj(Experiment.fromPars,
                                                     ['name', 'wavelength', 'offset', 'phase',
                                                      'background', 'resolution', 'measured_pattern'],
                                                     [calculator_experiment_name, wavelength, offset, scale[0],
                                                      backgrounds, resolution, data])

            # Fix up phase scale, but it is a terrible way of doing things.....
            experiment['phase'][calculator_experiment.phase.label[0]] = experiment['phase'][calculator_experiment_name]
            experiment['phase'][calculator_experiment.phase.label[0]]['scale'].refine = scale[0].refinement
            experiment['phase'][calculator_experiment.phase.label[0]]['scale']['store']['hide'] = scale[
                0].constraint_flag
            experiment['phase'][calculator_experiment.phase.label[0]]['name'] = calculator_experiment.phase.label[0]
            experiment['phase'][calculator_experiment.phase.label[0]]['scale'][
                'mapping'] = mapping_exp + '.phase.scale[0]'
            del experiment['phase'][calculator_experiment_name]
            if len(scale) > 1:
                for idx, item in enumerate(calculator_experiment.phase.item[1:]):
                    experiment['phase'][item.label] = ExperimentPhase.fromPars(item.label, item.scale)
                    experiment['phase'][item.label]['scale']['mapping'] = mapping_exp + '.phase.scale[{}]'.format(idx)
                    experiment['phase'][item.label]['scale'].refine = scale[idx].refinement
                    experiment['phase'][item.label]['scale']['store']['hide'] = scale[idx].constraint_flag
                    experiment['phase'][item.label]['name'] = item.label
            experiment['wavelength']['mapping'] = mapping_exp + '.setup.wavelength'
            experiment['offset']['mapping'] = mapping_exp + '.setup.offset_ttheta'

            experiments.append(experiment)

        # logging.info(experiments)
        self._log.info(Experiments(experiments))

        return Experiments(experiments)

    def getCalculations(self) -> Calculations:
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) or self._cryspy_obj.experiments is None:
            return Calculations({})
        self._cryspy_obj.apply_constraint()
        calculations = []
        for calculator_experiment in self._cryspy_obj.experiments:
            calculator_experiment_name = calculator_experiment.data_name
            calculator_experiment_index = self._cryspy_obj.experiments.index(calculator_experiment)

            # Calculated data
            self._log.debug("+++++++++> start")
            calculated_pattern, calculated_bragg_peaks, _ = calculator_experiment.calc_profile(
                np.array(calculator_experiment.meas.ttheta),
                self._cryspy_obj.crystals)
            self._log.debug("<+++++++++ end")

            # Bragg peaks
            offset = self._cryspy_obj.experiments[calculator_experiment_index].setup.offset_ttheta
            bragg_peaks = []
            for index, phase_info in enumerate(calculator_experiment.phase.item):
                def getCrystal():
                    for crystal in self._cryspy_obj.crystals:
                        if crystal.data_name == phase_info.label:
                            return crystal
                    return None

                crystal = getCrystal()
                if crystal is None:
                    raise KeyError

                bragg_peaks.append(CrystalBraggPeaks(crystal.data_name,
                                                     calculated_bragg_peaks[index].index_h,
                                                     calculated_bragg_peaks[index].index_k,
                                                     calculated_bragg_peaks[index].index_l,
                                                     (np.array(
                                                         calculated_bragg_peaks[index].ttheta) + offset).tolist()))
            bragg_peaks = BraggPeaks(bragg_peaks)

            # Calculated diffraction pattern
            x_calc = np.array(calculated_pattern.ttheta).tolist()
            if calculator_experiment.meas.intensity[0] is not None:
                y_obs = np.array(calculator_experiment.meas.intensity)
                sy_obs = np.array(calculator_experiment.meas.intensity_sigma)
                ###y_calc = np.array(calculated_pattern.intensity_total)
                y_calc_up = np.array(calculated_pattern.intensity_up_total)
                ###y_calc_down = np.array(calculated_pattern.intensity_down_total)
                y_calc = y_calc_up  ###+ y_calc_down
            elif calculator_experiment.meas.intensity_up[0] is not None:
                y_obs_up = np.array(calculator_experiment.meas.intensity_up)
                sy_obs_up = np.array(calculator_experiment.meas.intensity_up_sigma)
                y_obs_down = np.array(calculator_experiment.meas.intensity_down)
                sy_obs_down = np.array(calculator_experiment.meas.intensity_down_sigma)
                y_obs = y_obs_up + y_obs_down
                sy_obs = np.sqrt(np.square(sy_obs_up) + np.square(sy_obs_down))
                y_calc_up = np.array(calculated_pattern.intensity_up_total)
                y_calc_down = np.array(calculated_pattern.intensity_down_total)
                y_calc = y_calc_up + y_calc_down
            y_obs_upper = y_obs + sy_obs
            y_obs_lower = y_obs - sy_obs
            y_diff_upper = y_obs + sy_obs - y_calc
            y_diff_lower = y_obs - sy_obs - y_calc

            limits = Limits(y_obs_lower, y_obs_upper, y_diff_upper, y_diff_lower, x_calc, y_calc)
            calculated_pattern = CalculatedPattern(x_calc, y_calc, y_diff_lower, y_diff_upper)

            calculations.append(Calculation(calculator_experiment_name,
                                            bragg_peaks, calculated_pattern, limits))
        calculations = Calculations(calculations)

        self._log.info(calculations)

        return calculations

    @staticmethod
    def _setCalculatorObjFromProjectDict(item: cryspy.common.cl_fitable.Fitable, data: Base):
        if not isinstance(item, cryspy.common.cl_fitable.Fitable):
            return
        item.value = data.value
        item.refinement = data['store']['refine']

    @staticmethod
    def _createProjDictFromObj(item: 'PathDict', obj: cryspy.common.cl_fitable.Fitable):
        """ ... """
        item.setItemByPath(['store', 'value'], obj)
        if not isinstance(obj, cryspy.common.cl_fitable.Fitable):
            item.setItemByPath(['store', 'value'], obj)
        item.setItemByPath(['store', 'value'], obj.value)
        item.setItemByPath(['store', 'error'], obj.value)
        item.setItemByPath(['store', 'constraint'], obj.value)
        item.setItemByPath(['store', 'hide'], obj.value)
        item.setItemByPath(['store', 'refine'], obj.value)

    def setPhases(self, phases: Phases):
        """Set phases (sample model tab in GUI)"""
        self._log.info('-> start')
        self._cryspy_obj.crystals = []
        for phase_name in phases.keys():
            self.addPhase(phases[phase_name])
        self._log.info('<- end')

    def setExperiments(self, experiments: Experiments):
        """Set experiments (Experimental data tab in GUI)"""
        self._log.info('-> start')
        self._cryspy_obj.experiments = []
        for experiment_name in experiments.keys():
            self.addExperiment(experiments[experiment_name])
        self._log.info('<- end')

    def setObjFromProjectDicts(self, phases: Phases, experiments: Experiments):
        """Set all the cryspy parameters from project dictionary"""
        self.setPhases(phases)
        self.setExperiments(experiments)

    def asCifDict(self) -> dict:
        """..."""
        experiments = {}
        calculations = {}
        phases = {}
        if isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            if self._cryspy_obj.experiments is not None:
                experiments = "data_" + self._cryspy_obj.experiments[0].data_name + "\n\n" + \
                              self._cryspy_obj.experiments[0].params_to_cif() + "\n" + self._cryspy_obj.experiments[
                                  0].data_to_cif()  # temporarily solution, as params_to_cif, data_to_cif and calc_to_cif are not implemented yet in cryspy 0.2.0
                calculations = self._cryspy_obj.experiments[0].calc_to_cif()
            if self._cryspy_obj.crystals is not None:
                phases = self._cryspy_obj.crystals[0].to_cif()
        return {
            'phases': phases,
            'experiments': experiments,
            'calculations': calculations
        }

    @time_it
    def refine(self):
        """refinement ..."""
        refinement_res = self._cryspy_obj.refine()
        scipy_refinement_res = refinement_res['res']

        return refinement_res, scipy_refinement_res

    def getChiSq(self) -> Tuple[float, float]:
        chi_sq = 0.0
        n_res = 1
        # TODO this is bull, why is it like this!!!! :-(
        if self._cryspy_obj.experiments is not None:
            for calculator_experiment in self._cryspy_obj.experiments:
                chi_sq, n_res = calculator_experiment.calc_chi_sq(self._cryspy_obj.crystals)

        return chi_sq, n_res

    @property
    def final_chi_square(self) -> float:
        chi_sq, n_res = self.getChiSq()
        return chi_sq / n_res

    def _mappedValueUpdater(self, item_str, value):
        aeval = Interpreter(usersyms=dict(self=self))
        item = aeval(item_str)
        item.value = value

    def _mappedRefineUpdater(self, item_str, value):
        aeval = Interpreter(usersyms=dict(self=self))
        item = aeval(item_str)
        item.refinement = value

    def getProjectName(self) -> str:
        try:
            name = self._main_rcif["name"].value
        except TypeError:
            name = ''
        return name

    def getPhaseNames(self) -> list:
        return self._phase_name

    @time_it
    def addPhase(self, phase: Phase):
        phase_obj = self._createPhaseObj(phase)
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.crystals = [phase_obj, *self._cryspy_obj.crystals]
        else:
            self._cryspy_obj.crystals = [phase_obj]
        self._phase_name = [phase.data_name for phase in self._cryspy_obj.crystals]
        self._cryspy_obj.apply_constraint()

    @time_it
    def addExperiment(self, experiment: Experiment):
        exp_obj = self._createExperimentObj(experiment)
        if self._cryspy_obj.experiments is not None:
            self._cryspy_obj.experiments = [exp_obj, *self._cryspy_obj.experiments]
        else:
            self._cryspy_obj.experiments = [exp_obj]
        self._experiment_name = [experiment.data_name for experiment in self._cryspy_obj.experiments]

    @staticmethod
    def _createPhaseObj(phase: Phase):
        this_cell = cpCell(length_a=phase['cell']['length_a'].value,
                           length_b=phase['cell']['length_b'].value,
                           length_c=phase['cell']['length_c'].value,
                           angle_alpha=phase['cell']['angle_alpha'].value,
                           angle_beta=phase['cell']['angle_beta'].value,
                           angle_gamma=phase['cell']['angle_gamma'].value)

        this_space_group = cpSpaceGroup(name_hm_alt=phase['spacegroup']['space_group_name_HM_alt'].value,
                                        it_number=phase['spacegroup']['space_group_IT_number'].value,
                                        it_coordinate_system_code=phase['spacegroup']['origin_choice'].value,
                                        crystal_system=phase['spacegroup']['crystal_system'].value)

        this_atoms = []
        this_adp = []
        this_msp = []
        for atomLabel in phase['atoms'].keys():
            atom = phase['atoms'][atomLabel]
            this_atoms.append(
                AtomSite(label=atomLabel, type_symbol=atom['type_symbol'],
                         fract_x=atom['fract_x'].value, fract_y=atom['fract_y'].value,
                         fract_z=atom['fract_z'].value,
                         occupancy=atom['occupancy'].value, adp_type=atom['adp_type'].value,
                         u_iso_or_equiv=atom['U_iso_or_equiv'].value)
            )
            if atom['ADP']['u_11'].value is not None:
                this_adp.append(
                    AtomSiteAniso(label=atomLabel, u_11=atom['ADP']['u_11'].value,
                                  u_22=atom['ADP']['u_22'].value, u_33=atom['ADP']['u_33'].value,
                                  u_12=atom['ADP']['u_12'].value, u_13=atom['ADP']['u_13'].value,
                                  u_23=atom['ADP']['u_23'].value)
                )
            if atom['MSP']['type'].value is not None:
                this_msp.append(
                    AtomSiteSusceptibility(label=atomLabel, chi_type=atom['MSP']['type'].value,
                                           chi_11=atom['MSP']['chi_11'].value,
                                           chi_22=atom['MSP']['chi_22'].value, chi_33=atom['MSP']['chi_33'].value,
                                           chi_12=atom['MSP']['chi_12'].value, chi_13=atom['MSP']['chi_13'].value,
                                           chi_23=atom['MSP']['chi_23'].value)
                )

        this_atoms = AtomSiteL(this_atoms)
        this_adp = AtomSiteAnisoL(this_adp)
        this_msp = AtomSiteSusceptibilityL(this_msp)

        phase_obj = Crystal(data_name=phase['phasename'], cell=this_cell, space_group=this_space_group,
                            atom_site=this_atoms,
                            atom_site_aniso=this_adp, atom_site_susceptibility=this_msp)
        phase_obj.apply_constraint()
        return phase_obj

    @staticmethod
    def _createExperimentObj(experiment: Experiment):
        # First create a background
        backgrounds = PdBackgroundL(
            list(
                map(
                    lambda key: PdBackground(ttheta=experiment['background'][key]['ttheta'],
                                             intensity=experiment['background'][key]['intensity'].value),
                    experiment['background'].keys()
                )
            )
        )

        # backgrounds = PdBackgroundL(backgrounds)
        # Resolution
        resolution = PdInstrResolution(u=experiment['resolution']['u'].value,
                                       v=experiment['resolution']['v'].value,
                                       w=experiment['resolution']['w'].value,
                                       x=experiment['resolution']['x'].value,
                                       y=experiment['resolution']['y'].value)

        # Measured pattern
        pol = lambda data: PdMeas(ttheta=data[0], intensity=data[1], intensity_sigma=data[2],
                                  intensity_up=data[3], intensity_up_sigma=data[4],
                                  intensity_down=data[5], intensity_down_sigma=data[6])

        non_pol = lambda data: PdMeas(ttheta=data[0], intensity=data[1], intensity_sigma=data[2])

        if experiment['measured_pattern'].isPolarised:
            pattern = PdMeasL(list(map(pol, zip(experiment['measured_pattern']['x'],
                                                experiment['measured_pattern']['y_obs'],
                                                experiment['measured_pattern']['sy_obs'],
                                                experiment['measured_pattern']['y_obs_up'],
                                                experiment['measured_pattern']['sy_obs_up'],
                                                experiment['measured_pattern']['y_obs_down'],
                                                experiment['measured_pattern']['sy_obs_down']))))
        else:
            pattern = PdMeasL(list(map(non_pol, zip(experiment['measured_pattern']['x'],
                                                    experiment['measured_pattern']['y_obs'],
                                                    experiment['measured_pattern']['sy_obs']))))

        # Associate it to a phase
        phases = PhaseL(
            list(
                map(
                    lambda key: cpPhase(label=key, scale=experiment['phase'][key]['scale'].value),
                    experiment['phase'].keys()
                )
            )
        )

        # Setup the instrument...
        instrument = Setup(wavelength=experiment['wavelength'].value, offset_ttheta=experiment['offset'].value)

        return Pd(data_name=experiment['name'], background=backgrounds, resolution=resolution, meas=pattern,
                  phase=phases, setup=instrument)

    def associatePhaseToExp(self, exp_name: str, phase_name: str, scale: float):
        cryspyPhase = cpPhase(label=phase_name, scale=scale)
        idx = self._experiment_name.index(exp_name)
        self._cryspy_obj.experiments[idx].phase = PhaseL([cryspyPhase, *self._cryspy_obj.experiments[idx].phase.item])
        self._log.info('Associated phase %s to experiment %s', phase_name, exp_name)

    def disassociatePhaseToExp(self, exp_name: str, phase_name: str):
        idx = self._experiment_name.index(exp_name)
        exp_phases = self._cryspy_obj.experiments[idx].phase
        exp_phases = PhaseL(
            [exp_phases.item[i] for i, item in enumerate(exp_phases.item) if exp_phases.items[i][0] != phase_name])
        self._cryspy_obj.experiments[idx].phase = exp_phases
        self._log.info('Disassociated phase %s from experiment %s', phase_name, exp_name)

    def getPhasesAssocatedToExp(self, exp_name: str) -> list:
        idx = self._experiment_name.index(exp_name)
        phases = self._cryspy_obj.experiments[idx].phase
        # THIS IS A HACK AS CRYSPY IS SGSHRGFHGHRTGYHT
        exp_phases = [item[0] for item in phases.items]
        return exp_phases