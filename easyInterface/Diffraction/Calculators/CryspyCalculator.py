import os
import logging

from typing import Tuple

import cryspy
import pycifstar

from asteval import Interpreter

from easyInterface.Diffraction.DataClasses.DataObj.Calculation import *
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import *
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import *
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import Base

from cryspy.scripts.cl_rhochi import RhoChi
from cryspy.cif_like.cl_crystal import Crystal
from cryspy.cif_like.cl_pd import Pd

from cryspy.corecif.cl_cell import Cell as cpCell
from cryspy.corecif.cl_atom_site import AtomSite, AtomSiteL
from cryspy.corecif.cl_atom_site_aniso import AtomSiteAniso, AtomSiteAnisoL
from cryspy.magneticcif.cl_atom_site_susceptibility import AtomSiteSusceptibility, AtomSiteSusceptibilityL

from cryspy.symcif.cl_space_group import SpaceGroup as cpSpaceGroup

PHASE_SEGMENT = "_phases"
EXPERIMENT_SEGMENT = "_experiments"

CALCULATOR_INFO = {
    'name': 'CrysPy',
    'version': '0.2.0',
    'url': 'https://github.com/ikibalin/cryspy'
}


class CryspyCalculator:
    def __init__(self, main_rcif_path: str):
        self._experiment_name = []
        self._main_rcif_path = main_rcif_path
        self._main_rcif = None
        self._phases_path = ""
        self._phase_name = []
        self._experiments_path = ""
        self._cryspy_obj = self._createCryspyObj()

    def calculatorInfo(self) -> dict:
        return CALCULATOR_INFO

    def _createCryspyObj(self):
        """Create cryspy object from separate rcif files"""
        phase_segment = self._parseSegment(PHASE_SEGMENT)
        full_rcif_content = self._parseSegment(EXPERIMENT_SEGMENT) + phase_segment
        # update the phase name global
        rho_chi = RhoChi().from_cif(full_rcif_content)
        if rho_chi is None:
            rho_chi = RhoChi()
        else:
            self._phase_name = [phase.data_name for phase in rho_chi.crystals]
        return rho_chi

    def _parseSegment(self, segment: str = "") -> str:
        """Parse the given segment info from the main rcif file"""
        if not segment:
            return ""
        if segment not in (PHASE_SEGMENT, EXPERIMENT_SEGMENT):
            return ""
        rcif_dir_name = os.path.dirname(self._main_rcif_path)
        self._main_rcif = pycifstar.read_star_file(self._main_rcif_path)
        rcif_content = ""
        if segment in str(self._main_rcif):
            segment_rcif_path = os.path.join(rcif_dir_name, self._main_rcif[segment].value)
            if os.path.isfile(segment_rcif_path):
                with open(segment_rcif_path, 'r') as f:
                    segment_rcif_content = f.read()
                    rcif_content += segment_rcif_content
        return rcif_content

    def setExpsDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self._experiments_path = exp_path
        rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(self._experiments_path):
            with open(self._experiments_path, 'r') as f:
                exp_rcif_content = f.read()
                rcif_content += exp_rcif_content

        experiment = Pd.from_cif(exp_rcif_content)
        self._cryspy_obj.experiments = [experiment]
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.experiments[0].phase.items[0] = (self._phase_name[0])

    def addExpsDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self._experiments_path = exp_path
        exp_rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(self._experiments_path):
            with open(self._experiments_path, 'r') as f:
                exp_rcif_content = f.read()

        experiment = Pd.from_cif(exp_rcif_content)
        if self._cryspy_obj.experiments is not None:
            self._cryspy_obj.experiments = [*self._cryspy_obj.experiments, experiment]
        else:
            print(self._cryspy_obj.crystals)
            self._experiment_name.append(experiment.data_name)
            print(experiment.data_name)
            self._cryspy_obj.experiments = [experiment]
            print(self._cryspy_obj.crystals)
            if self._cryspy_obj.crystals is not None:
                self._cryspy_obj.experiments[0].phase.items[0] = (self._phase_name[0])

    def removeExpsDefinition(self, name: str):
        if name in self._experiment_name:
            index = self._experiment_name.index(name)
            self._experiment_name.pop(index)
            experiments = self._cryspy_obj.experiments
            experiments.pop(index)
            self._cryspy_obj.experiments = experiments
        else:
            raise KeyError

    def setPhaseDefinition(self, phases_path):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self._phases_path = phases_path
        rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(self._phases_path):
            with open(self._phases_path, 'r') as f:
                phases_rcif_content = f.read()
                rcif_content += phases_rcif_content

        # find the name of the new phase
        phase = Crystal().from_cif(phases_rcif_content)
        new_phase_name = phase.data_name
        self._cryspy_obj.crystals = [phase]
        self._phase_name = [new_phase_name]

        experiment_segment = ''
        if isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) and len(self._cryspy_obj.experiments) > 0:
            # TODO note only the first exp
            experiment_segment = self._cryspy_obj.experiments[0].to_cif()
            # Concatenate the corrected experiment and the new CIF
            rcif_content = rcif_content + "\n" + experiment_segment
            # This will update the CrysPy object
            self._cryspy_obj.from_cif(rcif_content)
            #
            self._cryspy_obj.experiments[0].phase.items[0] = (new_phase_name)

    def addPhaseDefinition(self, phases_path):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self._phases_path = phases_path
        phases_rcif_content = ""

        # This will read the CIF file
        if os.path.isfile(phases_path):
            with open(phases_path, 'r') as f:
                phases_rcif_content = f.read()

        # find the name of the new phase
        phase = Crystal().from_cif(phases_rcif_content)
        if self._cryspy_obj.crystals is not None:
            self._cryspy_obj.crystals = [*self._cryspy_obj.crystals, phase]
        else:
            self._cryspy_obj.crystals = [phase]
        self._phase_name.append(phase.data_name)

    def removePhaseDefinition(self, name: str):
        if name in self._phase_name:
            index = self._phase_name.index(name)
            self._phase_name.pop(index)
            phases = list(self._cryspy_obj.crystals)
            phases.pop(index)
            self._cryspy_obj.crystals = phases
        else:
            raise KeyError

    def writeMainCif(self, saveDir):
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            return
        main_block = self._main_rcif
        if self._cryspy_obj.crystals is not None:
            main_block["_phases"].value = 'phases.cif'
        if self._cryspy_obj.experiments is not None:
            main_block["_experiments"].value = 'experiments.cif'
        main_block.to_file(os.path.join(saveDir, 'main.cif'))

    def writePhaseCif(self, saveDir):
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            return
        phases_block = pycifstar.Global()
        # TODO write output for multiple phases
        if self._cryspy_obj.crystals is not None:
            phases_block.take_from_string(self._cryspy_obj.crystals[0].to_cif())
        phases_block.to_file(os.path.join(saveDir, 'phases.cif'))

    def writeExpCif(self, saveDir):
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi):
            return
        exp_block = pycifstar.Global()
        if self._cryspy_obj.experiments is not None:
            exp_block.take_from_string(self._cryspy_obj.experiments[0].to_cif())
        exp_block.to_file(os.path.join(saveDir, 'experiments.cif'))

    def saveCifs(self, saveDir):
        self.writeMainCif(saveDir)
        self.writePhaseCif(saveDir)
        self.writeExpCif(saveDir)

    @staticmethod
    def _createProjItemFromObj(func, keys: list, obj_list: list):
        """ ... """
        retVals = func(
            *[item.value if isinstance(item, cryspy.common.cl_fitable.Fitable) else item for item in obj_list])
        for index, key in enumerate(keys):
            if not isinstance(obj_list[index], cryspy.common.cl_fitable.Fitable):
                continue
            elif isinstance(retVals[key], Base):
                retVals.setItemByPath([key, 'store', 'error'], obj_list[index].sigma)
                retVals.setItemByPath([key, 'store', 'constraint'], obj_list[index].constraint)
                retVals.setItemByPath([key, 'store', 'hide'], obj_list[index].constraint_flag)
                retVals.setItemByPath([key, 'store', 'refine'], obj_list[index].refinement)
        return retVals

    def getPhases(self) -> Phases:
        """Set phases (sample model tab in GUI)"""

        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) or self._cryspy_obj.crystals is None:
            return Phases({})

        phases = []

        self._cryspy_obj.apply_constraint()

        # logging.info(self._cryspy_obj.crystals)
        mapping_base = 'self._cryspy_obj.crystals'

        for i, calculator_phase in enumerate(self._cryspy_obj.crystals):
            calculator_phase_name = calculator_phase.data_name
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

            # Unit cell parameters
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

            phase = Phase.fromPars(calculator_phase_name, space_group, unit_cell)
            # logging.info(phase)

            atoms = []
            # Atom sites
            for i, label in enumerate(calculator_phase.atom_site.label):
                calculator_atom_site = calculator_phase.atom_site
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
                    if i <= len(calculator_phase.atom_site_aniso.u_11):
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

                atoms.append(atom)

            atoms = Atoms(atoms)
            for key in atoms:
                phase['atoms'][key] = atoms[key]

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
            phases.append(phase)

        # logging.info(phases)
        logging.info(Phases(phases))

        return Phases(phases)

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
            scale = calculator_experiment.phase.scale[0]  # ONLY 1st scale parameter is currently taken into account!!!

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
                                                     [calculator_experiment_name, wavelength, offset, scale,
                                                      backgrounds, resolution, data])

            experiment['wavelength']['mapping'] = mapping_exp + '.setup.wavelength'
            experiment['offset']['mapping'] = mapping_exp + '.setup.offset_ttheta'
            experiment['phase']['scale']['mapping'] = mapping_exp + '.phase.scale[0]'

            experiments.append(experiment)

        # logging.info(experiments)
        logging.info(Experiments(experiments))

        return Experiments(experiments)

    def getCalculations(self) -> Calculations:
        if not isinstance(self._cryspy_obj, cryspy.scripts.cl_rhochi.RhoChi) or self._cryspy_obj.experiments is None:
            return Calculations({})

        calculations = []
        for calculator_experiment in self._cryspy_obj.experiments:
            calculator_experiment_name = calculator_experiment.data_name
            calculator_experiment_index = self._cryspy_obj.experiments.index(calculator_experiment)

            # Calculated data
            logging.info("+++++++++> start")
            calculated_pattern, calculated_bragg_peaks, _ = calculator_experiment.calc_profile(
                np.array(calculator_experiment.meas.ttheta),
                self._cryspy_obj.crystals)
            logging.info("<+++++++++ end")

            # Bragg peaks
            offset = self._cryspy_obj.experiments[calculator_experiment_index].setup.offset_ttheta
            bragg_peaks = []
            for index, crystal in enumerate(self._cryspy_obj.crystals):
                # TODO We need to check that each phase is in each experiment
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

        logging.info(calculations)

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

        logging.info('-> start')

        for phase_name in phases.keys():
            cryspy_phase_names = [crystal.data_name for crystal in self._cryspy_obj.crystals]
            if phase_name in cryspy_phase_names:
                cryspy_phase_index = cryspy_phase_names.index(phase_name)
                calculator_phase = self._cryspy_obj.crystals[cryspy_phase_index]

                project_phase = phases[phase_name]

                # Unit cell parameters
                calculator_cell = calculator_phase.cell
                project_cell = project_phase['cell']
                self._setCalculatorObjFromProjectDict(calculator_cell.length_a, project_cell['length_a'])
                self._setCalculatorObjFromProjectDict(calculator_cell.length_b, project_cell['length_b'])
                self._setCalculatorObjFromProjectDict(calculator_cell.length_c, project_cell['length_c'])
                self._setCalculatorObjFromProjectDict(calculator_cell.angle_alpha, project_cell['angle_alpha'])
                self._setCalculatorObjFromProjectDict(calculator_cell.angle_beta, project_cell['angle_beta'])
                self._setCalculatorObjFromProjectDict(calculator_cell.angle_gamma, project_cell['angle_gamma'])

                # Atom sites
                for i, label in enumerate(calculator_phase.atom_site.label):
                    calculator_atom_site = calculator_phase.atom_site
                    project_atom_site = project_phase['atoms'][label]

                    # Atom site coordinates
                    self._setCalculatorObjFromProjectDict(calculator_atom_site.fract_x[i], project_atom_site['fract_x'])
                    self._setCalculatorObjFromProjectDict(calculator_atom_site.fract_y[i], project_atom_site['fract_y'])
                    self._setCalculatorObjFromProjectDict(calculator_atom_site.fract_z[i], project_atom_site['fract_z'])

                    # Atom site occupancy
                    self._setCalculatorObjFromProjectDict(calculator_atom_site.occupancy[i],
                                                          project_atom_site['occupancy'])

                    # Atom site isotropic ADP
                    self._setCalculatorObjFromProjectDict(calculator_atom_site.u_iso_or_equiv[i],
                                                          project_atom_site['U_iso_or_equiv'])

                # Atom site anisotropic ADP
                if calculator_phase.atom_site_aniso is not None:
                    for i, label in enumerate(calculator_phase.atom_site_aniso.label):
                        calculator_atom_site = calculator_phase.atom_site_aniso
                        project_atom_site = project_phase['atoms'][label]['ADP']
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_11[i], project_atom_site['u_11'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_22[i], project_atom_site['u_22'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_33[i], project_atom_site['u_33'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_12[i], project_atom_site['u_12'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_13[i], project_atom_site['u_13'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.u_23[i], project_atom_site['u_23'])

                # Atom site MSP
                if calculator_phase.atom_site_susceptibility is not None:
                    for i, label in enumerate(calculator_phase.atom_site_susceptibility.label):
                        calculator_atom_site = calculator_phase.atom_site_susceptibility
                        project_atom_site = project_phase['atoms'][label]['MSP']
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_type[i],
                                                              project_atom_site['type'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_11[i],
                                                              project_atom_site['chi_11'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_22[i],
                                                              project_atom_site['chi_22'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_33[i],
                                                              project_atom_site['chi_33'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_12[i],
                                                              project_atom_site['chi_12'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_13[i],
                                                              project_atom_site['chi_13'])
                        self._setCalculatorObjFromProjectDict(calculator_atom_site.chi_23[i],
                                                              project_atom_site['chi_23'])
            else:
                self.addPhase(phases[phase_name])
        logging.info('<- end')

    def setExperiments(self, experiments: Experiments):
        """Set experiments (Experimental data tab in GUI)"""
        logging.info('-> start')

        for experiment_name in experiments.keys():
            cryspy_experiment_names = [experiment.data_name for experiment in self._cryspy_obj.experiments]
            if experiment_name in cryspy_experiment_names:

                cryspy_experiment_index = cryspy_experiment_names.index(experiment_name)
                calculator_experiment = self._cryspy_obj.experiments[cryspy_experiment_index]
                project_experiment = experiments[experiment_name]

                # Experimental setup
                calculator_setup = calculator_experiment.setup
                self._setCalculatorObjFromProjectDict(calculator_setup.wavelength, project_experiment['wavelength'])
                self._setCalculatorObjFromProjectDict(calculator_setup.offset_ttheta, project_experiment['offset'])

                # Scale
                # ONLY 1st scale parameter is currently taken into account!!!
                self._setCalculatorObjFromProjectDict(calculator_experiment.phase.scale[0],
                                                      project_experiment['phase']['scale'])

                # Background
                calculator_background = calculator_experiment.background
                project_background = project_experiment['background']

                for index, background in enumerate(project_background.values()):
                    self._setCalculatorObjFromProjectDict(calculator_background.ttheta[index], background['intensity'])

                # Instrument resolution
                project_resolution = project_experiment['resolution']
                calculator_resolution = calculator_experiment.resolution
                self._setCalculatorObjFromProjectDict(calculator_resolution.u, project_resolution['u'])
                self._setCalculatorObjFromProjectDict(calculator_resolution.v, project_resolution['v'])
                self._setCalculatorObjFromProjectDict(calculator_resolution.w, project_resolution['w'])
                self._setCalculatorObjFromProjectDict(calculator_resolution.x, project_resolution['x'])
                self._setCalculatorObjFromProjectDict(calculator_resolution.y, project_resolution['y'])
            else:
                raise NotImplementedError
        logging.info('<- end')

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

    def _mappedValueUpdater(self, itemStr, value):
        aeval = Interpreter(usersyms=dict(self=self))
        item = aeval(itemStr)
        item.value = value

    def _mappedRefineUpdater(self, itemStr, value):
        aeval = Interpreter(usersyms=dict(self=self))
        item = aeval(itemStr)
        item.refinement = value

    def getProjectName(self) -> str:
        return self._main_rcif["name"].value

    def getPhaseNames(self) -> list:
        return self._phase_name

    def addPhase(self, phase: Phase):

        thisCell = cpCell(length_a=phase['cell']['length_a'].value,
                          length_b=phase['cell']['length_b'].value,
                          length_c=phase['cell']['length_c'].value,
                          angle_alpha=phase['cell']['angle_alpha'].value,
                          angle_beta=phase['cell']['angle_beta'].value,
                          angle_gamma=phase['cell']['angle_gamma'].value)

        thisSpaceGroup = cpSpaceGroup(name_hm_alt=phase['spacegroup']['space_group_name_HM_alt'].value,
                                      it_number=phase['spacegroup']['space_group_IT_number'].value,
                                      it_coordinate_system_code=phase['spacegroup']['origin_choice'].value,
                                      crystal_system=phase['spacegroup']['crystal_system'].value)

        thisAtoms = []
        thisADP = []
        thisMSP = []
        for atomLabel in phase['atoms'].keys():
            atom = phase['atoms'][atomLabel]
            thisAtoms.append(
                AtomSite(label=atomLabel, type_symbol=atom['type_symbol'],
                         fract_x=atom['fract_x'].value, fract_y=atom['fract_y'].value, fract_z=atom['fract_z'].value,
                         occupancy=atom['occupancy'].value, adp_type=atom['adp_type'].value,
                         u_iso_or_equiv=atom['U_iso_or_equiv'].value)
            )
            if atom['ADP']['u_11'].value is not None:
                thisADP.append(
                    AtomSiteAniso(label=atomLabel, u_11=atom['ADP']['u_11'].value,
                                  u_22=atom['ADP']['u_22'].value, u_33=atom['ADP']['u_33'].value,
                                  u_12=atom['ADP']['u_12'].value, u_13=atom['ADP']['u_13'].value,
                                  u_23=atom['ADP']['u_23'].value)
                )
            if atom['MSP']['type'].value is not None:
                thisMSP.append(
                    AtomSiteSusceptibility(label=atomLabel, chi_type=atom['MSP']['type'].value,
                                           chi_11=atom['MSP']['chi_11'].value,
                                           chi_22=atom['MSP']['chi_22'].value, chi_33=atom['MSP']['chi_33'].value,
                                           chi_12=atom['MSP']['chi_12'].value, chi_13=atom['MSP']['chi_13'].value,
                                           chi_23=atom['MSP']['chi_23'].value)
                )

        thisAtoms = AtomSiteL(thisAtoms)
        thisADP = AtomSiteAnisoL(thisADP)
        thisMSP = AtomSiteSusceptibilityL(thisMSP)

        phaseObj = Crystal(data_name=phase['phasename'], cell=thisCell, space_group=thisSpaceGroup, atom_site=thisAtoms,
                           atom_site_aniso=thisADP, atom_site_susceptibility=thisMSP)

        self._cryspy_obj.crystals = [phaseObj, *self._cryspy_obj.crystals]
        self._phase_name = [phase.data_name for phase in self._cryspy_obj.crystals]
