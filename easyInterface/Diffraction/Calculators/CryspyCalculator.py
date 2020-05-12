#  Licensed under the GNU General Public License v3.0
#  Copyright (c) of the author (github.com/wardsimon)
#  Created: 12/3/2020

import os, re
from typing import Tuple, Optional

import cryspy
import pycifstar
from asteval import Interpreter
from cryspy.cif_like.cl_crystal import Crystal
from cryspy.cif_like.cl_pd import Pd, PdBackground, PdBackgroundL, PdInstrResolution, PdMeas, PdMeasL, PhaseL, Setup, \
    Chi2, DiffrnRadiation
from cryspy.cif_like.cl_pd import Phase as cryspyPhase
from cryspy.corecif.cl_atom_site import AtomSite, AtomSiteL
from cryspy.corecif.cl_atom_site_aniso import AtomSiteAniso, AtomSiteAnisoL
# Imports needed to create a phase
from cryspy.corecif.cl_cell import Cell as cryspyCell
from cryspy.magneticcif.cl_atom_site_susceptibility import AtomSiteSusceptibility, AtomSiteSusceptibilityL
## Start cryspy imports
# Imports needed to create a cryspyObj
from cryspy.scripts.cl_rhochi import RhoChi
from cryspy.symcif.cl_space_group import SpaceGroup as cpSpaceGroup
from easyInterface.Diffraction.DataClasses.DataObj.Calculation import *
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import *
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import *
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import Base
from easyInterface.Utils.Helpers import time_it

# Version info
cryspy_version = 'Undefined'
try:
    from cryspy import __version__ as cryspy_version, Fitable, AtomSiteScat, AtomSiteScatL
except ImportError:
    logging.logger.info('Can not find cryspy version. Using default text')
CALCULATOR_INFO = {
    'name': 'CrysPy',
    'version': cryspy_version,
    'url': 'https://github.com/ikibalin/cryspy'
}

PHASE_SEGMENT = "_phases"
EXPERIMENT_SEGMENT = "_experiments"


class CryspyCalculator:
    def __init__(self, main_rcif_path: Union[str, type(None)] = None) -> None:
        self._log = logging.getLogger(__class__.__module__)
        self._experiment_names = []
        self._main_rcif_path = main_rcif_path
        self._main_rcif = None
        self._phases_path = ""
        self._phase_names = []
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
        if not self._main_rcif_path:
            return RhoChi()
        try:
            phase_segment = self._parseSegment(PHASE_SEGMENT)
        except TypeError:
            self._log.warning('Main cif location is not a path')
            return RhoChi()
        try:
            exp_segment = self._parseSegment(EXPERIMENT_SEGMENT)
        except TypeError:
            self._log.warning('Main cif location is not a path')
            return RhoChi()
        full_rcif_content = exp_segment + phase_segment
        # update the phase name global
        self._log.debug('Calling RhoChi')
        rho_chi = RhoChi().from_cif(full_rcif_content)
        if rho_chi is None:
            self._log.debug('Main CIF is empty')
            rho_chi = RhoChi()
        else:
            self._log.debug('Populating _phase_name with cryspy phase names')
            self._phase_names = [phase.data_name for phase in rho_chi.crystals]
            self._experiment_names = [experiment.data_name for experiment in rho_chi.experiments]
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

    def setExpsDefinition(self, exp_path: str) -> NoReturn:
        """
        Set an experiment/s to be simulated from a cif file. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_path: Path to a experiment file (`.cif`)
        """
        self._log.debug('----> Start')
        exp_rcif_content = ""
        if not isinstance(exp_path, (str, os.PathLike)):
            self._log.warning('Experiment definition is not a string or path')
            return

        # This will read the CIF file
        if os.path.isfile(exp_path):
            with open(exp_path, 'r') as f:
                self._log.debug('Reading experiment cif file')
                exp_rcif_content = f.read()
            self._experiments_path = exp_path
        else:
            self._log.warning('Experiment cif can not be found')
            return

        experiment = Pd.from_cif(exp_rcif_content)
        if experiment is None:
            self._log.error('Experiment cif data is malformed')
        self._cryspy_obj.experiments = [experiment]
        self._experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        self._log.info('Setting cryspy experiments from cif content')
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.experiments[0].phase.items[0] = (self._phase_names[0])
        self._log.debug('<---- End')

    def addExpDefinitionFromString(self, exp_rcif_content: str) -> NoReturn:
        """
        Set an experiment/s to be simulated from a string. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_rcif_content: String containing the contents of an experiment file (`.cif`)
        """
        self._log.debug('----> Start')
        experiment = Pd.from_cif(exp_rcif_content)
        if experiment is None:
            self._log.error('Experiment cif data is malformed')
        if self._cryspy_obj.experiments is None:
            self._cryspy_obj.experiments = [experiment]
        else:
            self._cryspy_obj.experiments = [*self._cryspy_obj.experiments, experiment]
        self._experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        self._log.debug('<---- End')

    def addExpsDefinition(self, exp_path: str) -> NoReturn:
        """
        Add an experiment to be simulated from a cif file. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_path: Path to a experiment file (`.cif`)
        """
        self._log.debug('----> Start')
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
        if experiment is None:
            self._log.error('Experiment cif data is malformed')
        if self._cryspy_obj.experiments is not None:
            self._log.info('Adding experiment to cryspy experiments')
            # Check for the same name and modify if exist
            if experiment.data_name in self._experiment_names:
                index = 0
                new_name = experiment.data_name
                while new_name in self._experiment_names:
                    new_name = experiment.data_name + str(index)
                    index += 1
                self._log.warning(f'Experiment {experiment.data_name} exists, renaming to {new_name}')
                experiment.data_name = new_name
            self._cryspy_obj.experiments = [*self._cryspy_obj.experiments, experiment]
        else:
            self._log.info('Experiment set from cif content')
            self._cryspy_obj.experiments = [experiment]
        self._experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        self._log.debug('<---- End')

    def removeExpsDefinition(self, experiment_name: str) -> NoReturn:
        """
        Remove a experiment from both the project dictionary and the calculator.

        :param experiment_name: Name of the experiment to be removed.
        """
        self._log.debug('----> Start')
        if experiment_name in self._experiment_names:
            self._log.info('Experiment found, removing')
            experiments = self._cryspy_obj.experiments
            self._cryspy_obj.experiments = [experiment for experiment in experiments if
                                            experiment.data_name != experiment_name]
            self._experiment_names = []
            if self._cryspy_obj.experiments:
                self._experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]
        else:
            raise KeyError
        self._log.debug('<---- End')

    def setPhaseDefinition(self, phases_path: str) -> NoReturn:
        """
        Parse a phases cif file and replace existing crystal phases

        :param phases_path: Path to new phase definition file  (`.cif`)
        """
        self._log.debug('----> Start')
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
        self._phase_names = [phase.data_name for phase in self._cryspy_obj.crystals]

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

    def addPhaseDefinitionFromString(self, phase_rcif_content: str) -> NoReturn:
        """
        Set an experiment/s to be simulated from a string. Note that this will not have any crystallographic phases
        associated with it.

        :param phase_rcif_content: String containing the contents of a phase file (`.cif`)
        """
        self._log.debug('----> Start')
        phase = Crystal().from_cif(phase_rcif_content)
        self._log.warning(f"self._cryspy_obj.crystals: {self._cryspy_obj.crystals}")
        if phase is None:
            self._log.error('Phase cif data is malformed')
        if self._cryspy_obj.crystals is None:
            self._cryspy_obj.crystals = [phase]
            #self._log.warning(f"self._cryspy_obj.crystals: {self._cryspy_obj.crystals}")
        else:
            self._cryspy_obj.crystals = [*self._cryspy_obj.crystals, phase]
            self._log.warning(f"self._cryspy_obj.crystals: {self._cryspy_obj.crystals}")
        self._phase_names = [phase.data_name for phase in self._cryspy_obj.crystals]
        self._log.debug('<---- End')

    def addPhaseDefinition(self, phases_path: str) -> NoReturn:
        """
        Add new phases from a cif file to the list of existing crystal phases in the calculator.

        :param phases_path: Path to a phase definition file (`.cif`)
        """
        self._log.debug('----> Start')
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
            # Check for the same name and modify if exist
            if phase.data_name in self._phase_names:
                index = 0
                new_name = phase.data_name
                while new_name == self._experiment_names:
                    new_name = phase.data_name + '_' + str(index)
                    index += 1
                self._log.warning(f'Phase {phase.data_name} exists, renaming to {new_name}')
                phase.data_name = new_name
            self._cryspy_obj.crystals = [*self._cryspy_obj.crystals, phase]
        else:
            self._log.info('Setting cryspy crystal to phase')
            self._cryspy_obj.crystals = [phase]
        self._phase_names = [phase.data_name for phase in self._cryspy_obj.crystals]
        self._log.debug('<---- End')

    def removePhaseDefinition(self, phase_name: str) -> NoReturn:
        """
        Remove a phase of a given name from the calculator object.

        :param phase_name: name of the phase to be removed.
        """
        self._log.debug('----> Start')
        if phase_name in self._phase_names:
            crystals = self._cryspy_obj.crystals
            self._cryspy_obj.crystals = [crystal for crystal in crystals if crystal.data_name != phase_name]
            self._phase_names = []
            if self._cryspy_obj.crystals:
                self._phase_names = [phase.data_name for phase in self._cryspy_obj.crystals]
            self._log.info('Removing phase %s', phase_name)
        else:
            self._log.warning('Phase not found in cryspy crystals')
            raise KeyError
        # See if this is associated to an experiment....
        for experiment in self._cryspy_obj.experiments:
            if phase_name in self.getPhasesAssocatedToExp(experiment.data_name):
                self.disassociatePhaseFromExp(experiment.data_name, phase_name)
        self._log.debug('<---- End')

    def blockToCif(self, block: 'pycifstar.global_.Global') -> str:
        """
        Returns a cleaned up data block as text string.

        :param block: cif data block.
        :return: cleaned up data block as text string.
        """
        text = str(block)
        text = re.sub("global_\s+", "", text)
        text = re.sub("\n{3}", "\n\n", text)
        return text

    def writeMainCif(self, save_dir: str, main_filename: str = 'main.cif', phase_filename: str = 'phases.cif',
                     exp_filename: str = 'experiments.cif', calc_filename: str = 'calculations.cif') -> NoReturn:
        """
        Write the `main.cif` where links to the experiments and phases are stored and other generalised project
        information.

        :param save_dir: Directory to where the main cif file should be saved.
        :param main_filename:  What to call the main file.
        :param phase_filename: What to call the phases file.
        :param exp_filename: What to call the experiments file.
        :param calc_filename: What to call the calculations file.
        """
        self._log.debug('----> Start')
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        if self._cryspy_obj.crystals is not None:
            self._main_rcif["_phases"].value = phase_filename
        if self._cryspy_obj.experiments is not None:
            self._main_rcif["_experiments"].value = exp_filename
            self._main_rcif["_calculations"].value = calc_filename
        save_to = os.path.join(save_dir, main_filename)
        try:
            self._log.info('Writing main cif file')
            with open(save_to, "w") as f:
                f.write(self.asCifDict()["main"])
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        except AttributeError:
            self._log.warning('No information stored in the object. Saving failed')
        self._log.debug('<---- End')

    def writePhaseCif(self, save_dir: str, phase_name: str = 'phases.cif') -> NoReturn:
        """
        Write the `phases.cif` where all phases in the calculator are saved to file. This cif file should be
        compatible with other crystallographic software.

        :param phase_name: What to call the phases file.
        :param save_dir: Directory to where the phases cif file should be saved.
        """
        self._log.debug('----> Start')
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        save_to = os.path.join(save_dir, phase_name)
        if self._cryspy_obj.crystals is None:
            self._log.info('No experiments to save. creating empty file: %s', save_to)
        try:
            self._log.info('Writing phases cif file')
            with open(save_to, "w") as f:
                f.write(self.asCifDict()["phases"])
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def writeExpCif(self, save_dir: str, exp_name: str = 'experiments.cif') -> NoReturn:
        """
        Write the `experiments.cif` where all experiments in the calculator are saved to file. This includes the
        instrumental parameters and which phases are in the experiment/s

        :param exp_name: What to call the experiments file.
        :param save_dir: Directory to where the experiment cif file should be saved.
        """
        self._log.debug('----> Start')
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        save_to = os.path.join(save_dir, exp_name)
        if self._cryspy_obj.experiments is None:
            self._log.info('No experiments to save. creating empty file: %s', save_to)
        try:
            self._log.info('Writing experiments cif file')
            with open(save_to, "w") as f:
                f.write(self.asCifDict()["experiments"])
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def writeCalcCif(self, save_dir: str, calc_name: str = 'calculations.cif') -> NoReturn:
        """
        Write the `calculations.cif` where all calculations in the calculator are saved to file.

        :param calc_name: What to call the calculations file.
        :param save_dir: Directory to where the calculations cif file should be saved.
        """
        self._log.debug('----> Start')
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            self._log.warning('Cryspy object is malformed. Failure...')
            self._log.debug('<---- End')
            return
        save_to = os.path.join(save_dir, calc_name)
        if self._cryspy_obj.experiments is None:
            self._log.info('No calculations to save. creating empty file: %s', save_to)
        try:
            self._log.info('Writing calculations cif file')
            with open(save_to, "w") as f:
                f.write(self.asCifDict()["calculations"])
        except PermissionError:
            self._log.warning('No permission to write to %s', save_to)
        self._log.debug('<---- End')

    def saveCifs(self, save_dir: str, main_name: str = 'main.cif', phase_name: str = 'phases.cif',
                 exp_name: str = 'experiments.cif', calc_name: str = 'calculations.cif') -> NoReturn:
        """
        Write project cif files (`main.cif`, `phases.cif`, `experiments.cif` and `calculations.cif`) to a user
        supplied directory. This contains all information needed to recreate the project dictionary.

        :param save_dir: Directory to where the main cif file should be saved.
        :param main_name:  What to call the main file.
        :param phase_name: What to call the phases file.
        :param exp_name: What to call the experiments file.
        :param calc_name: What to call the calculations file.
        """
        self._log.debug('----> Start')
        try:
            self.writeMainCif(save_dir, main_name)
            self.writePhaseCif(save_dir, phase_name)
            self.writeExpCif(save_dir, exp_name)
            self.writeCalcCif(save_dir, calc_name)
            self._log.info('Cifs saved successfully')
        except PermissionError:
            self._log.warning('Unable to save cifs')
        self._log.debug('<---- End')

    @staticmethod
    def _createProjItemFromObj(func, keys: list, obj_list: list) -> list:
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
        """
        Returns all phases from the calculator object.
        """
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) or self._cryspy_obj.crystals is None:
            return Phases({})

        self._cryspy_obj.apply_constraint()  # THIS IS 400ms !!!!!!
        phases = list(map(self._makePhase, self._cryspy_obj.crystals))
        phases = Phases(phases)
        self._log.info(phases)
        return phases

    def readPhaseDefinition(self, phases_path) -> Optional[Tuple[Phase, cryspyPhase]]:
        """
        Parse the relevant phases file and update the corresponding model
        """
        self._log.debug('----> Start')
        phases_rcif_content = ""
        if not isinstance(phases_path, (str, os.PathLike)):
            self._log.warning('Phase definition is not a string or path')
            return

        # This will read the CIF file
        if os.path.isfile(phases_path):
            with open(phases_path, 'r') as f:
                phases_rcif_content = f.read()
        phase_cp = cryspyPhase().from_cif(phases_rcif_content)
        phase = self._makePhase(phase_cp)
        self._log.debug('<---- End')
        return phase, phase_cp

    def _makePhase(self, calculator_phase: Crystal) -> Phase:
        # This is ~180ms per atom in phase. Limited by cryspy
        calculator_phase_name = calculator_phase.data_name
        # This group is < 1ms
        space_group = self._makePhasesSpaceGroup(calculator_phase)
        unit_cell = self._makePhaseCell(calculator_phase)
        phase = Phase.fromPars(calculator_phase_name, space_group, unit_cell)
        # Atom sites ~ 6ms
        atoms = list(map(lambda x: self._makeAtom(calculator_phase, x), calculator_phase.atom_site.label))
        atoms = Atoms(atoms)

        for key in atoms:
            phase['atoms'][key] = atoms[key]

        # This is ~125ms per atom due to cryspy taking ~110ms :-(
        self._makeAtomSites(phase, calculator_phase)
        return phase

    def _makeAtom(self, calculator_phase: Crystal, label: str) -> Atom:
        # This is ~2ms
        site_index = calculator_phase.atom_site.label.index(label)
        calculator_atom_site = calculator_phase.atom_site
        if self._cryspy_obj.crystals is not None:
            try:
                crystal_index = self._cryspy_obj.crystals.index(calculator_phase)
            except ValueError:
                # Phase has not been added to crystal. Assume that it will be, possibly in error :-/
                crystal_index = len(self._cryspy_obj.crystals)
        else:
            # There are no crystals yet. assume that it will be added.
            crystal_index = 0
        mapping_base = 'self._cryspy_obj.crystals'
        mapping_phase = mapping_base + '[{}]'.format(crystal_index)
        mapping_atom = mapping_phase + '.atom_site'

        # Atom sites symbol
        type_symbol = calculator_atom_site.type_symbol[site_index]

        # Atom site neutron scattering length
        scat_length_neutron = calculator_atom_site.scat_length_neutron[site_index]

        # Atom site coordinates
        fract_x = calculator_atom_site.fract_x[site_index]
        fract_y = calculator_atom_site.fract_y[site_index]
        fract_z = calculator_atom_site.fract_z[site_index]

        # Atom site occupancy
        occupancy = calculator_atom_site.occupancy[site_index]

        # Atom site ADP type
        adp_type = calculator_atom_site.adp_type[site_index]

        # Atom site isotropic ADP
        U_iso_or_equiv = calculator_atom_site.u_iso_or_equiv[site_index]

        # Atom site anisotropic ADP
        adp = None
        if calculator_phase.atom_site_aniso is not None:
            if site_index < len(calculator_phase.atom_site_aniso.u_11):
                mapping_adp = mapping_phase + '.atom_site_aniso'

                adp = [calculator_phase.atom_site_aniso.u_11[site_index],
                       calculator_phase.atom_site_aniso.u_22[site_index],
                       calculator_phase.atom_site_aniso.u_33[site_index],
                       calculator_phase.atom_site_aniso.u_12[site_index],
                       calculator_phase.atom_site_aniso.u_13[site_index],
                       calculator_phase.atom_site_aniso.u_23[site_index]]
                adp = self._createProjItemFromObj(ADP.fromPars,
                                                  ['u_11', 'u_22', 'u_33',
                                                   'u_12', 'u_13', 'u_23'],
                                                  adp)
                adp['u_11']['mapping'] = mapping_adp + '.u_11[{}]'.format(site_index)
                adp['u_22']['mapping'] = mapping_adp + '.u_22[{}]'.format(site_index)
                adp['u_33']['mapping'] = mapping_adp + '.u_33[{}]'.format(site_index)
                adp['u_12']['mapping'] = mapping_adp + '.u_12[{}]'.format(site_index)
                adp['u_13']['mapping'] = mapping_adp + '.u_13[{}]'.format(site_index)
                adp['u_23']['mapping'] = mapping_adp + '.u_23[{}]'.format(site_index)

        # Atom site MSP
        msp = None
        if calculator_phase.atom_site_susceptibility is not None:
            if site_index < len(calculator_phase.atom_site_susceptibility.chi_type):
                mapping_msp = mapping_phase + '.atom_site_susceptibility'

                msp = [calculator_phase.atom_site_susceptibility.chi_type[site_index],
                       calculator_phase.atom_site_susceptibility.chi_11[site_index],
                       calculator_phase.atom_site_susceptibility.chi_22[site_index],
                       calculator_phase.atom_site_susceptibility.chi_33[site_index],
                       calculator_phase.atom_site_susceptibility.chi_12[site_index],
                       calculator_phase.atom_site_susceptibility.chi_13[site_index],
                       calculator_phase.atom_site_susceptibility.chi_23[site_index]]
                msp = self._createProjItemFromObj(MSP.fromPars,
                                                  ['MSPtype', 'chi_11', 'chi_22', 'chi_33',
                                                   'chi_12', 'chi_13', 'chi_23'],
                                                  msp)
                msp['type']['mapping'] = mapping_msp + '.chi_type[{}]'.format(site_index)
                msp['chi_11']['mapping'] = mapping_msp + '.chi_11[{}]'.format(site_index)
                msp['chi_22']['mapping'] = mapping_msp + '.chi_22[{}]'.format(site_index)
                msp['chi_33']['mapping'] = mapping_msp + '.chi_33[{}]'.format(site_index)
                msp['chi_12']['mapping'] = mapping_msp + '.chi_12[{}]'.format(site_index)
                msp['chi_13']['mapping'] = mapping_msp + '.chi_13[{}]'.format(site_index)
                msp['chi_23']['mapping'] = mapping_msp + '.chi_23[{}]'.format(site_index)

        # Add an atom to atoms
        atom = self._createProjItemFromObj(
            Atom.fromPars,
            ['atom_site_label', 'type_symbol', 'scat_length_neutron',
             'fract_x', 'fract_y', 'fract_z', 'occupancy', 'adp_type',
             'U_iso_or_equiv'],
            [label, type_symbol, scat_length_neutron,
             fract_x, fract_y, fract_z, occupancy, adp_type,
             U_iso_or_equiv, adp, msp])

        atom['scat_length_neutron']['mapping'] = mapping_atom + '.scat_length_neutron[{}]'.format(site_index)
        atom['fract_x']['mapping'] = mapping_atom + '.fract_x[{}]'.format(site_index)
        atom['fract_y']['mapping'] = mapping_atom + '.fract_y[{}]'.format(site_index)
        atom['fract_z']['mapping'] = mapping_atom + '.fract_z[{}]'.format(site_index)
        atom['occupancy']['mapping'] = mapping_atom + '.occupancy[{}]'.format(site_index)
        atom['adp_type']['mapping'] = mapping_atom + '.adp_type[{}]'.format(site_index)
        atom['U_iso_or_equiv']['mapping'] = mapping_atom + '.u_iso_or_equiv[{}]'.format(site_index)
        return atom

    @staticmethod
    def _makeAtomSites(phase: Phase, calculator_phase: Crystal) -> NoReturn:
        atom_site_list = [[], [], [], []]
        # Atom sites for structure view (all the positions inside unit cell of 1x1x1)
        for x, y, z, scat_length_neutron in zip(calculator_phase.atom_site.fract_x,
                                                calculator_phase.atom_site.fract_y,
                                                calculator_phase.atom_site.fract_z,
                                                calculator_phase.atom_site.scat_length_neutron):
            x_array, y_array, z_array, _ = calculator_phase.space_group.calc_xyz_mult(x.value, y.value, z.value)
            scat_length_neutron_array = np.full_like(x_array, scat_length_neutron, dtype=complex)
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

        # convert complex numbers into strings without brackets to be recognizable in GUI
        scat_length_neutron_str_array = [str(item)[1:-1] for item in atom_site_list[3]]

        phase.setItemByPath(['sites', 'fract_x'], atom_site_list[0])
        phase.setItemByPath(['sites', 'fract_y'], atom_site_list[1])
        phase.setItemByPath(['sites', 'fract_z'], atom_site_list[2])
        phase.setItemByPath(['sites', 'scat_length_neutron'], scat_length_neutron_str_array)

    def _getPhasesSpaceGroup(self, phase_name: str) -> SpaceGroup:
        i = self._phase_names.index(phase_name)
        calculator_phase = self._cryspy_obj.crystals[i]
        space_group = self._makePhasesSpaceGroup(calculator_phase, i)
        return space_group

    def _makePhasesSpaceGroup(self, calculator_phase: Crystal, index=None) -> SpaceGroup:
        mapping_base = 'self._cryspy_obj.crystals'
        i = 0
        if index is not None:
            i = self._phase_names.index(calculator_phase.data_name)
        # logging.info(calculator_phase_name)
        mapping_phase = mapping_base + '[{}]'.format(i)
        # Space group
        space_group = self._createProjItemFromObj(SpaceGroup.fromPars,
                                                  ['crystal_system', 'space_group_name_HM_ref',
                                                   'space_group_IT_number', 'origin_choice'],
                                                  [calculator_phase.space_group.crystal_system,
                                                   calculator_phase.space_group.name_hm_ref,
                                                   calculator_phase.space_group.it_number,
                                                   calculator_phase.space_group.it_coordinate_system_code])

        space_group['crystal_system']['mapping'] = mapping_phase + '.space_group.crystal_system'
        space_group['space_group_name_HM_ref']['mapping'] = mapping_phase + '.space_group.name_hm_ref'
        space_group['space_group_IT_number']['mapping'] = mapping_phase + '.space_group.it_number'
        space_group['origin_choice']['mapping'] = mapping_phase + '.space_group.it_coordinate_system_code'
        return space_group

    def _makePhaseCell(self, calculator_phase: Crystal, index=None) -> Cell:
        mapping_base = 'self._cryspy_obj.crystals'
        i = 0
        if index is not None:
            i = self._phase_names.index(calculator_phase.data_name)
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

    def _getPhaseCell(self, phase_name: str) -> Cell:
        i = self._phase_names.index(phase_name)
        calculator_phase = self._cryspy_obj.crystals[i]
        unit_cell = self._makePhaseCell(calculator_phase, i)
        return unit_cell

    def getExperimentFromCif(self, cif_string) -> Experiment:
        cryspy_experiment = Pd.from_cif(cif_string)
        new_exp = self._makeExperiment(cryspy_experiment)
        return new_exp

    def getPhaseFromCif(self, cif_string) -> Phase:
        cryspy_phase = Crystal.from_cif(cif_string)
        new_phase = self._makePhase(cryspy_phase)
        return new_phase

    @time_it
    def getExperiments(self) -> Experiments:
        """
        Returns all experiments from the calculator object.
        """
        experiments = []

        if self._cryspy_obj.experiments is None:
            return Experiments({})

        for i, calculator_experiment in enumerate(self._cryspy_obj.experiments):
            experiment = self._makeExperiment(calculator_experiment, i)
            experiments.append(experiment)

        # logging.info(experiments)
        self._log.info(Experiments(experiments))

        return Experiments(experiments)

    def getCalculations(self) -> Calculations:
        """
        Returns all calculations from the calculator object.
        """
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
                y_calc_up = np.array(calculated_pattern.intensity_up_total)
                y_calc_down = np.array(calculated_pattern.intensity_down_total)
                y_calc_bkg = np.array(calculated_pattern.intensity_bkg_calc)
            if calculator_experiment.meas.intensity_up[0] is not None:
                y_obs_up = np.array(calculator_experiment.meas.intensity_up)
                sy_obs_up = np.array(calculator_experiment.meas.intensity_up_sigma)
                y_obs_down = np.array(calculator_experiment.meas.intensity_down)
                sy_obs_down = np.array(calculator_experiment.meas.intensity_down_sigma)
                y_obs = y_obs_up + y_obs_down
                sy_obs = np.sqrt(np.square(sy_obs_up) + np.square(sy_obs_down))
                y_calc_up = np.array(calculated_pattern.intensity_up_total)
                y_calc_down = np.array(calculated_pattern.intensity_down_total)
                y_calc_bkg = np.multiply(np.array(calculated_pattern.intensity_bkg_calc), 2)
            y_calc = y_calc_up + y_calc_down
            y_obs_upper = y_obs + sy_obs
            y_obs_lower = y_obs - sy_obs
            y_diff_upper = y_obs + sy_obs - y_calc
            y_diff_lower = y_obs - sy_obs - y_calc

            limits = Limits(y_obs_lower, y_obs_upper, y_diff_upper, y_diff_lower, x_calc, y_calc)
            calculated_pattern = CalculatedPattern(x_calc, y_diff_lower, y_diff_upper, y_calc_up, y_calc_down,
                                                   y_calc_bkg)

            calculations.append(Calculation(calculator_experiment_name,
                                            bragg_peaks, calculated_pattern, limits))
        calculations = Calculations(calculations)

        self._log.info(calculations)

        return calculations

    @staticmethod
    def _setCalculatorObjFromProjectDict(item: cryspy.common.cl_fitable.Fitable, data: Base) -> NoReturn:
        if not isinstance(item, cryspy.common.cl_fitable.Fitable):
            return
        item.value = data.value
        item.refinement = data['store']['refine']

    @staticmethod
    def _createProjDictFromObj(item: 'PathDict', obj: cryspy.common.cl_fitable.Fitable) -> NoReturn:
        """ ... """
        item.setItemByPath(['store', 'value'], obj)
        if not isinstance(obj, cryspy.common.cl_fitable.Fitable):
            item.setItemByPath(['store', 'value'], obj)
        item.setItemByPath(['store', 'value'], obj.value)
        item.setItemByPath(['store', 'error'], obj.value)
        item.setItemByPath(['store', 'constraint'], obj.value)
        item.setItemByPath(['store', 'hide'], obj.value)
        item.setItemByPath(['store', 'refine'], obj.value)

    def setPhases(self, phases: Phases) -> NoReturn:
        """Set phases (sample model tab in GUI)"""
        self._log.info('-> start')
        self._cryspy_obj.crystals = []
        for phase_name in phases.keys():
            self.addPhase(phases[phase_name])
        self._log.info('<- end')

    def setExperiments(self, experiments: Experiments) -> NoReturn:
        """Set experiments (Experimental data tab in GUI)"""
        self._log.info('-> start')
        self._cryspy_obj.experiments = []
        for experiment_name in experiments.keys():
            self.addExperiment(experiments[experiment_name])
        self._log.info('<- end')

    def setObjFromProjectDicts(self, phases: Phases, experiments: Experiments) -> NoReturn:
        """Set all the cryspy parameters from project dictionary"""
        self.setPhases(phases)
        self.setExperiments(experiments)
        cif = self._cryspy_obj.to_cif()
        self._cryspy_obj = RhoChi().from_cif(cif)

    def asCifDict(self) -> dict:
        """Returns dict of all the CIFs"""
        main = ""
        phases = ""
        experiments = ""
        calculations = ""
        if isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            # main.cif
            if self._main_rcif is not None:
                main = self.blockToCif(self._main_rcif)
            # phases.cif
            if self._cryspy_obj.crystals is not None:
                for phase in self._cryspy_obj.crystals:
                    phases += phase.to_cif() + '\n'
            # experiments.cif & calculations.cif
            if self._cryspy_obj.experiments is not None:
                for experiment in self._cryspy_obj.experiments:
                    experiments += "data_" + experiment.data_name + "\n\n" + \
                                   experiment.params_to_cif() + "\n" + \
                                   experiment.data_to_cif()
                    calculations += "data_" + experiment.data_name + "\n\n" + \
                                    experiment.calc_to_cif()
        return { 'main': main, 'phases': phases, 'experiments': experiments, 'calculations': calculations }

    @time_it
    def refine(self) -> Tuple[dict, dict]:
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

    def _mappedValueUpdater(self, item_str, value) -> NoReturn:
        aeval = Interpreter(usersyms=dict(self=self))
        item = aeval(item_str)
        item.value = value

    def _mappedRefineUpdater(self, item_str, value) -> NoReturn:
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
        return self._phase_names

    @time_it
    def addPhase(self, phase: Phase) -> NoReturn:
        phase_obj = self._createPhaseObj(phase)
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.crystals = [phase_obj, *self._cryspy_obj.crystals]
        else:
            self._cryspy_obj.crystals = [phase_obj]
        self._phase_names = [phase.data_name for phase in self._cryspy_obj.crystals]
        self._cryspy_obj.apply_constraint()

    @time_it
    def addExperiment(self, experiment: Experiment) -> NoReturn:
        exp_obj = self._createExperimentObj(experiment)
        if self._cryspy_obj.experiments is not None:
            self._cryspy_obj.experiments = [exp_obj, *self._cryspy_obj.experiments]
        else:
            self._cryspy_obj.experiments = [exp_obj]
        self._experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]

    @staticmethod
    def _createPhaseObj(phase: Phase) -> Crystal:

        def convRefine(cp_in, easy_in, cp_keys, e_keys):
            for cp_param, e_param in zip(cp_keys, e_keys):
                if isinstance(easy_in[e_param], Base):
                    cp_obj = getattr(cp_in, cp_param)
                    if isinstance(cp_obj, Fitable):
                        setattr(cp_obj, 'refinement', easy_in[e_param].refine)

        d = dict()
        d['data_name'] = phase['phasename']
        cell = dict()
        cell['length_a'] = phase['cell']['length_a'].value
        cell['length_b'] = phase['cell']['length_b'].value
        cell['length_c'] = phase['cell']['length_c'].value
        cell['angle_alpha'] = phase['cell']['angle_alpha'].value
        cell['angle_beta'] = phase['cell']['angle_beta'].value
        cell['angle_gamma'] = phase['cell']['angle_gamma'].value
        d['cell'] = cryspyCell(**cell)
        convRefine(d['cell'], phase['cell'],
                   ['length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma'],
                   ['length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma'])

        spg = dict()
        # spg['name_hm_ref'] = phase['spacegroup']['space_group_name_HM_ref'].value
        spg['it_number'] = phase['spacegroup']['space_group_IT_number'].value
        spg['it_coordinate_system_code'] = phase['spacegroup']['origin_choice'].value
        # spg['crystal_system'] = phase['spacegroup']['crystal_system'].value
        d['space_group'] = cpSpaceGroup(**spg)
        convRefine(d['space_group'], phase['spacegroup'],
                   ['it_coordinate_system_code', 'it_number'],
                   ['origin_choice', 'space_group_IT_number'])

        this_atoms = []
        this_adp = []
        this_msp = []
        for atom_label in phase['atoms'].keys():
            atom = phase['atoms'][atom_label]
            atom_site = dict()
            atom_site['label'] = atom_label
            atom_site['type_symbol'] = atom['type_symbol']
            atom_site['fract_x'] = atom['fract_x'].value
            atom_site['fract_y'] = atom['fract_y'].value
            atom_site['fract_z'] = atom['fract_z'].value
            atom_site['occupancy'] = atom['occupancy'].value
            atom_site['adp_type'] = atom['adp_type'].value
            atom_site['u_iso_or_equiv'] = atom['U_iso_or_equiv'].value
            a_site = AtomSite(**atom_site)
            convRefine(a_site, atom,
                       ['type_symbol', 'fract_x', 'fract_y', 'fract_z', 'occupancy', 'adp_type', 'u_iso_or_equiv'],
                       ['type_symbol', 'fract_x', 'fract_y', 'fract_z', 'occupancy', 'adp_type', 'U_iso_or_equiv'])
            this_atoms.append(a_site)
            if atom['ADP']['u_11'].value is not None:
                adp = dict()
                adp['label'] = atom_label
                adp['u_11'] = atom['ADP']['u_11'].value
                adp['u_22'] = atom['ADP']['u_22'].value
                adp['u_33'] = atom['ADP']['u_33'].value
                adp['u_12'] = atom['ADP']['u_12'].value
                adp['u_13'] = atom['ADP']['u_13'].value
                adp['u_23'] = atom['ADP']['u_23'].value
                adp = AtomSiteAniso(**adp)
                convRefine(adp, atom['ADP'],
                           ['u_11', 'u_22', 'u_33', 'u_12', 'u_13', 'u_23'],
                           ['u_11', 'u_22', 'u_33', 'u_12', 'u_13', 'u_23'])
                this_adp.append(adp)
            if atom['MSP']['type'].value is not None:
                msp = dict()
                msp['label'] = atom_label
                msp['chi_type'] = atom['MSP']['type'].value
                msp['chi_11'] = atom['MSP']['chi_11'].value
                msp['chi_22'] = atom['MSP']['chi_22'].value
                msp['chi_33'] = atom['MSP']['chi_33'].value
                msp['chi_12'] = atom['MSP']['chi_12'].value
                msp['chi_13'] = atom['MSP']['chi_13'].value
                msp['chi_23'] = atom['MSP']['chi_23'].value
                msp = AtomSiteSusceptibility(**msp)
                convRefine(msp, atom['MSP'],
                           ['chi_11', 'chi_22', 'chi_33', 'chi_12', 'chi_13', 'chi_23'],
                           ['chi_11', 'chi_22', 'chi_33', 'chi_12', 'chi_13', 'chi_23'])
                this_msp.append(msp)

        d['atom_site'] = AtomSiteL(this_atoms)
        if len(this_adp) > 0:
            d['atom_site_aniso'] = AtomSiteAnisoL(this_adp)
        if len(this_msp) > 0:
            d['atom_site_susceptibility'] = AtomSiteSusceptibilityL(this_msp)
            # This means that it's magnetic, so it must have a atom_site_scat
            d['atom_site_scat'] = AtomSiteScatL([AtomSiteScat(label=msp.label) for msp in this_msp])

        phase_obj = Crystal(**d)
        phase_obj.apply_constraint()
        return phase_obj

    def _createExperimentObj(self, experiment: Experiment) -> Pd:
        # First create a background

        exp = dict()
        exp['data_name'] = experiment['name']

        def bg_mapper(key):
            bg = PdBackground(ttheta=experiment['background'][key]['ttheta'],
                              intensity=experiment['background'][key]['intensity'].value)
            bg.intensity.refinement = experiment['background'][key]['intensity'].refine
            return bg

        bg_keys = [float(key) for key in experiment['background'].keys()]
        bg_keys.sort()
        exp['background'] = PdBackgroundL(
            list(map(lambda key: bg_mapper(str(key)), bg_keys))
        )

        # backgrounds = PdBackgroundL(backgrounds)
        # Resolution
        exp['resolution'] = PdInstrResolution(u=experiment['resolution']['u'].value,
                                              v=experiment['resolution']['v'].value,
                                              w=experiment['resolution']['w'].value,
                                              x=experiment['resolution']['x'].value,
                                              y=experiment['resolution']['y'].value)
        exp['resolution'].u.refinement = experiment['resolution']['u'].refine
        exp['resolution'].v.refinement = experiment['resolution']['v'].refine
        exp['resolution'].w.refinement = experiment['resolution']['w'].refine
        exp['resolution'].x.refinement = experiment['resolution']['x'].refine
        exp['resolution'].y.refinement = experiment['resolution']['y'].refine

        # Measured pattern
        pol = lambda data: PdMeas(ttheta=data[0],
                                  intensity_up=data[1], intensity_up_sigma=data[2],
                                  intensity_down=data[3], intensity_down_sigma=data[4])

        non_pol = lambda data: PdMeas(ttheta=data[0], intensity=data[1], intensity_sigma=data[2])

        if experiment['measured_pattern'].isPolarised:
            pattern = PdMeasL(list(map(pol, zip(experiment['measured_pattern']['x'],
                                                experiment['measured_pattern']['y_obs_up'],
                                                experiment['measured_pattern']['sy_obs_up'],
                                                experiment['measured_pattern']['y_obs_down'],
                                                experiment['measured_pattern']['sy_obs_down']))))
            exp['chi2'] = Chi2(sum=experiment['chi2'].sum, diff=experiment['chi2'].diff, up=False, down=False)
            exp['diffrn_radiation'] = DiffrnRadiation(polarization=experiment['polarization']['polarization'].value,
                                                      efficiency=experiment['polarization']['efficiency'].value)
            exp['diffrn_radiation'].polarization.refinement = experiment['polarization']['polarization'].refine
            exp['diffrn_radiation'].efficiency.refinement = experiment['polarization']['efficiency'].refine
        else:
            pattern = PdMeasL(list(map(non_pol, zip(experiment['measured_pattern']['x'],
                                                    experiment['measured_pattern']['y_obs'],
                                                    experiment['measured_pattern']['sy_obs']))))

        exp['meas'] = pattern

        def phase_mapper(key):
            phase = cryspyPhase(label=key, scale=experiment['phase'][key]['scale'].value, igsize=0)
            phase.scale.refinement = experiment['phase'][key]['scale'].refine
            return phase

        # Associate it to a phase
        exp['phase'] = PhaseL([phase_mapper(key) for key in experiment['phase'].keys()])
        # Setup the instrument...
        if experiment['measured_pattern'].isPolarised:
            exp['setup'] = Setup(wavelength=experiment['wavelength'].value, offset_ttheta=experiment['offset'].value,
                                 field=experiment['field'].value)

        else:
            exp['setup'] = Setup(wavelength=experiment['wavelength'].value, offset_ttheta=experiment['offset'].value)
        exp['setup'].wavelength.refinement = experiment['wavelength'].refine
        exp['setup'].offset_ttheta.refinement = experiment['offset'].refine
        return Pd(**exp)

    def associatePhaseToExp(self, exp_name: str, phase_name: str, scale: float, igsize: float = 0.0) -> NoReturn:
        cryspyPhaseObj = cryspyPhase(label=phase_name, scale=scale, igsize=igsize)
        idx = self._experiment_names.index(exp_name)
        self._cryspy_obj.experiments[idx].phase = PhaseL(
            [cryspyPhaseObj, *self._cryspy_obj.experiments[idx].phase.item])
        self._log.info('Associated phase %s to experiment %s', phase_name, exp_name)

    def disassociatePhaseFromExp(self, exp_name: str, phase_name: str) -> NoReturn:
        idx = self._experiment_names.index(exp_name)
        exp_phases = self._cryspy_obj.experiments[idx].phase
        exp_phases = PhaseL(
            [exp_phases.item[i] for i, item in enumerate(exp_phases.item) if exp_phases.items[i][0] != phase_name])
        self._cryspy_obj.experiments[idx].phase = exp_phases
        self._log.info('Disassociated phase %s from experiment %s', phase_name, exp_name)

    def getPhasesAssocatedToExp(self, exp_name: str) -> list:
        idx = self._experiment_names.index(exp_name)
        phases = self._cryspy_obj.experiments[idx].phase
        # THIS IS A HACK AS CRYSPY IS SGSHRGFHGHRTGYHT
        exp_phases = [item[0] for item in phases.items]
        return exp_phases

    def _makeExperiment(self, calculator_experiment, i=0) -> Experiment:

        mapping_base = 'self._cryspy_obj.experiments'
        calculator_experiment_name = calculator_experiment.data_name
        mapping_exp = mapping_base + '[{}]'.format(i)

        # Experimental setup
        calculator_setup = calculator_experiment.setup
        wavelength = calculator_setup.wavelength
        offset = calculator_setup.offset_ttheta

        is_polarised = hasattr(calculator_setup, 'field')
        field = None
        if is_polarised:
            field = calculator_setup.field
            chi2 = {'sum': True, 'diff': False, 'up': False, 'down': False}
            rad = {'polarization': 0, 'efficiency': 1}
            for obj in calculator_experiment.optional_objs:
                if isinstance(obj, Chi2):
                    for key in chi2.keys():
                        chi2[key] = getattr(obj, key)
                elif isinstance(obj, DiffrnRadiation):
                    for key in rad.keys():
                        rad[key] = getattr(obj, key)
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
        backgrounds.sort(key=lambda x: float(x['ttheta']))
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
        y_obs_diff = None
        sy_obs_diff = None
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
            y_obs_diff = (y_obs_up - y_obs_down).tolist()
            sy_obs_diff = np.sqrt(np.square(sy_obs_up) + np.square(sy_obs_down)).tolist()
            y_obs_up = y_obs_up.tolist()
            y_obs_down = y_obs_down.tolist()
            sy_obs = np.sqrt(np.square(sy_obs_up) + np.square(sy_obs_down)).tolist()

        data = MeasuredPattern(x_obs, y_obs, sy_obs, y_obs_diff, sy_obs_diff, y_obs_up, sy_obs_up, y_obs_down,
                               sy_obs_down)

        experiment = self._createProjItemFromObj(Experiment.fromPars,
                                                 ['name', 'wavelength', 'offset', 'phase',
                                                  'background', 'resolution', 'measured_pattern', 'field'],
                                                 [calculator_experiment_name, wavelength, offset, scale[0],
                                                  backgrounds, resolution, data, field])

        if data.isPolarised:
            options = ['sum', 'diff']
            experiment['chi2'].set_object(calculator_experiment.chi2)
            for option in options:
                if getattr(calculator_experiment.chi2, option):
                    setattr(experiment['chi2'], option, True)
            experiment['polarization'][
                'polarization'].value = calculator_experiment.diffrn_radiation.polarization.value
            experiment['polarization']['polarization']['store'][
                'error'] = calculator_experiment.diffrn_radiation.polarization.sigma

            experiment['polarization'][
                'polarization'].refine = calculator_experiment.diffrn_radiation.polarization.refinement
            experiment['polarization']['polarization']['store']['hide'] = False
            experiment['polarization']['polarization']['mapping'] = mapping_exp + '.diffrn_radiation.polarization'
            experiment['polarization']['efficiency'].value = calculator_experiment.diffrn_radiation.efficiency.value
            experiment['polarization'][
                'efficiency'].refine = calculator_experiment.diffrn_radiation.efficiency.refinement
            experiment['polarization']['efficiency']['store'][
                'error'] = calculator_experiment.diffrn_radiation.efficiency.sigma
            experiment['polarization']['efficiency']['store']['hide'] = False
            experiment['polarization']['efficiency']['mapping'] = mapping_exp + '.diffrn_radiation.efficiency'

            # updateMinMax method is called only when polarization object is created in
            # Experiment.py (Line 430): polarization=Polarization.default(). The default values
            # of polarization.polarization and polarization.efficiency = 1.0 at that moment, so
            # min and max are defined as 0.8 and 1.2, respectively.
            # Now, we need to reset min and max and call updateMinMax() again!
            experiment['polarization']['polarization'].min = -np.Inf
            experiment['polarization']['polarization'].max = np.Inf
            experiment['polarization']['polarization'].updateMinMax()
            experiment['polarization']['efficiency'].min = -np.Inf
            experiment['polarization']['efficiency'].max = np.Inf
            experiment['polarization']['efficiency'].updateMinMax()

            # Fix up phase scale, but it is a terrible way of doing things.....
        phase_label = calculator_experiment.phase.label[0]
        experiment['phase'][phase_label] = experiment['phase'][calculator_experiment_name]
        experiment['phase'][phase_label]['scale'].refine = scale[0].refinement
        experiment['phase'][phase_label]['scale']['store']['hide'] = scale[0].constraint_flag
        experiment['phase'][phase_label]['name'] = phase_label
        experiment['phase'][phase_label]['scale']['mapping'] = mapping_exp + '.phase.scale[0]'
        del experiment['phase'][calculator_experiment_name]
        if len(scale) > 0:
            for idx, item in enumerate(calculator_experiment.phase.item[0:]):
                experiment['phase'][item.label] = ExperimentPhase.fromPars(item.label, scale[idx].value)
                experiment['phase'][item.label]['scale']['mapping'] = mapping_exp + '.phase.scale[{}]'.format(idx)
                experiment['phase'][item.label]['scale'].refine = scale[idx].refinement
                experiment['phase'][item.label]['scale']['store']['hide'] = scale[idx].constraint_flag
                experiment['phase'][item.label]['scale']['store']['error'] = scale[idx].sigma
                experiment['phase'][item.label]['name'] = item.label
        experiment['wavelength']['mapping'] = mapping_exp + '.setup.wavelength'
        experiment['offset']['mapping'] = mapping_exp + '.setup.offset_ttheta'
        experiment['field']['mapping'] = mapping_exp + '.setup.field'

        return experiment
