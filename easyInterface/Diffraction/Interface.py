__author__ = 'simonward'
__version__ = "2020_02_01"

import os
from datetime import datetime
from copy import deepcopy
from typing import List, Callable, Any, Union

from easyInterface.Diffraction.DataClasses.DataObj.Calculation import Calculation, Calculations
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import Experiments, Experiment, ExperimentPhase
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases, Phase
from easyInterface.Utils.DictTools import UndoableDict
from easyInterface.Diffraction.DataClasses.Utils.InfoObjs import Interface, App, Calculator, Info
from easyInterface.Utils.Helpers import time_it
from easyInterface import logger as logging

from numpy import datetime64

class ProjectDict(UndoableDict):
    """
    This class deals with the creation and modification of the main project dictionary.
    """

    def __init__(self, interface: Interface, app: App, calculator: Calculator, info: Info, phases: Phases,
                 experiments: Experiments, calculations: Calculations):
        """
        Create the main project dictionary from base constituent classes. Generally called from one of the constructor
        methods.

        :param app: Details of the EasyDiffraction app
        :param calculator: Calculator to be used, from Calculators class
        :param info: Store of ID's and some fit information
        :param phases: Collection of crystallographic phases which make up the system
        :param experiments: Collection of experimental data to be simulated

        :return: Project dictionary which has undo/redo functionality
        """
        super().__init__(interface=interface, calculator=calculator, app=app, info=info, phases=phases,
                         experiments=experiments, calculations=calculations)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Created a project dictionary')

    @classmethod
    def default(cls) -> 'ProjectDict':
        """
        Create a default and empty project dictionary

        :return: Default project dictionary with undo/redo functionality
        """
        app = App.default()
        info = Info.default()
        calculator = Calculator.default()
        interface = Interface.default()
        phases = Phases({})
        experiments = Experiments({})
        calculations = Calculations({})
        return cls(interface, app, calculator, info, phases, experiments, calculations)

    @classmethod
    def fromPars(cls, experiments: Union[Experiments, Experiment, List[Experiment]],
                 phases: Union[Phases, Phase, List[Phase]],
                 calculations: Union[Calculations, Calculation, List[Calculation]]) -> 'ProjectDict':
        """
        Create a main project dictionary from phases and experiments.

        :param experiments: A collection of experiments to be compared to calculations
        :param phases: A Collection of crystallographic phases to be calculated

        :return: Project dictionary with undo/redo
        """
        app = App.default()
        info = Info.default()
        calculator = Calculator.default()
        interface = Interface.default()

        if not isinstance(experiments, Experiments):
            experiments = Experiments(experiments)
        if not isinstance(phases, Phases):
            phases = Phases(phases)
        if not isinstance(calculations, Calculations):
            calculations = Calculations(calculations)
        return cls(interface, app, calculator, info, phases, experiments, calculations)


class CalculatorInterface:
    """
    Interface to calculators in the `easyInterface.Diffraction.Calculator` class.
    """

    def __init__(self, calculator: 'easyInterface.Diffraction.Calculator'):
        """
        Initialise an interface with a `calculator` of the `easyInterface.Diffraction.Calculator` class.

        :param calculator: Calculator of the `easyInterface.Diffraction.Calculator` class.
        """

        self._log = logging.getLogger(__class__.__module__)
        self.project_dict = ProjectDict.default()
        self.calculator = calculator
        # Set the calculator info
        CALCULATOR_INFO = self.calculator.calculatorInfo()
        for key in CALCULATOR_INFO.keys():
            self.project_dict['calculator'][key] = CALCULATOR_INFO[key]
        self.__last_updated = datetime.max
        self.__last_calculated = datetime.min
        self.setProjectFromCalculator()
        self._log.info("Created: %s", self)

    def __repr__(self) -> str:
        return "easyInterface ({}) with calculator: {} - {}".format(
            self.project_dict['interface']['version'],
            self.project_dict['calculator']['name'],
            self.project_dict['calculator']['version'])

    @property
    def final_chi_square(self) -> float:
        """
        Calculates the final chi squared of the simulation. Where the final chi squared is the chi squared divided by
        the number of data points.

        :return: Final chi squared
        """
        return self.calculator.final_chi_square

    def setProjectFromCalculator(self):
        """
        Sets the project dictionary from the calculator given on initialisation. Calling this function will regenerate
        the project dictionary and changes may be lost.
        """
        self.updatePhases()
        self.updateExperiments()
        self.updateCalculations()
        try:
            self.project_dict.setItemByPath(['info', 'modified_datetime'],
                                            datetime.fromtimestamp(
                                                os.path.getmtime(self.calculator._main_rcif_path)).strftime(
                                                '%d %b %Y, %H:%M:%S'))
        except (TypeError, FileNotFoundError):
            self.project_dict.setItemByPath(['info', 'modified_datetime'], datetime.min)
        self.project_dict.setItemByPath(['info', 'name'], self.calculator.getProjectName())
        self.project_dict.setItemByPath(['info', 'refinement_datetime'], str(datetime64('now')))

        final_chi_square, n_res = self.calculator.getChiSq()
        final_chi_square = final_chi_square / n_res

        self.project_dict.setItemByPath(['info', 'n_res', 'store', 'value'], n_res)
        self.project_dict.setItemByPath(['info', 'chi_squared', 'store', 'value'], final_chi_square)
        self.__last_updated = datetime.now()

    ###
    # Setting of Calculator
    ###

    # Phase section
    def setPhaseDefinition(self, phase_path: str):
        """
        Parse a phases cif file and replace existing crystal phases

        :param phase_path: Path to new phase definition file  (`.cif`)

        Example::

            interface = CalculatorInterface(calculator)
            phase_path = '~/Experiments/phases.cif'
            interface.setPhaseDefinition(phase_path)
        """
        self.calculator.setPhaseDefinition(phase_path)
        # This will re-create all local directories
        self.updatePhases()
        self.updateExperiments()

    def addPhaseDefinition(self, phase_path: str):
        """
        Add a new phases from a cif file to the list of existing crystal phases.

        :param phase_path: Path to a phase definition file (`.cif`)

        Example::

            interface = CalculatorInterface(calculator)
            phase_path = '~/Experiments/new_phase.cif'
            interface.addPhaseDefinition(phase_path)
        """
        self.calculator.addPhaseDefinition(phase_path)
        self.updatePhases()

    def addPhase(self, phase: Phase):
        """
        Add a new phases from a cif file to the list of existing crystal phases.

        :param phase:
        """
        if phase['phasename'] in self.project_dict['phases'].keys():
            self.setPhase(phase)
        else:
            self.project_dict.setItemByPath(['phases', phase['phasename']], phase)
            self.calculator.addPhase(phase)
        self.__last_updated = datetime.now()

    def removePhase(self, phase_name: str):
        self.calculator.removePhaseDefinition(phase_name)
        self.project_dict.rmItemByPath(['phases', phase_name])
        self.__last_updated = datetime.now()

    def addPhaseToExp(self, exp_name: str, phase_name: str, scale: float = 0.0):
        self.calculator.associatePhaseToExp(exp_name, phase_name, scale)
        currentPhases = self.project_dict.getItemByPath(['experiments', 'phase'])
        newPhase = ExperimentPhase.fromPars(phase_name, scale)
        currentPhases[phase_name] = newPhase
        self.project_dict.setItemByPath(['experiments', 'phase'], currentPhases)
        self.__last_updated = datetime.now()

    def removePhaseFromExp(self, exp_name: str, phase_name: str):
        self.calculator.disassociatePhaseToExp(exp_name, phase_name)
        self.project_dict.rmItemByPath(['experiments', 'phase', phase_name])
        self.__last_updated = datetime.now()

    # Experiment section
    def setExperimentDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.setExpsDefinition(exp_path)
        # This will re-create all local directories
        self.updateExperiments()

    def addExperimentDefinition(self, exp_path: str):
        """
        Add an experiment to be simulated from a cif file. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_path: Path to a experiment file (`.cif`)
        """
        self.calculator.addExpsDefinition(exp_path)
        self.updateExperiments()

    def addExperiment(self, experiment: Experiment):
        if experiment['name'] in self.project_dict['experiments'].keys():
            self.setExperiment(experiment)
        else:
            self.project_dict.setItemByPath(['experiments', experiment['name']], experiment)
            self.calculator.setExperiments(self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def removeExperiment(self, experiment_name: str):
        self.calculator.removeExpsDefinition(experiment_name)
        self.updateExperiments()
        self.__last_updated = datetime.now()

    # Output section
    def writeMainCif(self, save_dir: str):
        """
        Write the `main.cif` where links to the experiments and phases are stored and other generalised project
        information.

        :param save_dir: Directory to where the main cif file should be saved.
        :return: None
        """
        self.calculator.writeMainCif(save_dir)

    def writePhaseCif(self, save_dir: str):
        """
        Write the `phases.cif` where all phases in the project dictionary are saved to file. This cif file should be
        compatible with other crystallographic software.

        :param save_dir: Directory to where the phases cif file should be saved.
        :return: None
        """
        self.calculator.writePhaseCif(save_dir)

    def writeExpCif(self, save_dir: str):
        """
        Write the `experiments.cif` where all experiments in the project dictionary are saved to file. This includes the
        instrumental parameters and which phases are in the experiment/s

        :param save_dir: Directory to where the experiment cif file should be saved.
        :return: None
        """
        self.calculator.writeExpCif(save_dir)

    def saveCifs(self, save_dir: str):
        """
        Write project cif files (`main.cif`, `experiments.cif` and `phases.cif`) to a user supplied directory. This
        contains all information needed to recreate the project dictionary.

        :param save_dir: Directory to where the project cif files should be saved.
        :return: None
        """
        self.writeMainCif(save_dir)
        self.writePhaseCif(save_dir)
        self.writeExpCif(save_dir)

    ###
    # Syncing between Calculator/Dict
    ###
    @time_it
    def updatePhases(self):
        """
        Synchronise the phases in project dictionary by queering the calculator object.

        :return: None
        """
        phases = self.calculator.getPhases()

        if len(self.project_dict['phases']) == 0:
            self.project_dict.startBulkUpdate('Bulk update of phases')
            self.project_dict.setItemByPath(['phases'], phases)
            self.project_dict.setItemByPath(['info', 'phase_ids'], list(phases.keys()))
            self.project_dict.endBulkUpdate()
        else:
            k, v = self.project_dict['phases'].dictComparison(phases)
            if not k:
                return

            k = [['phases', *key] for key in k]

            k.append(['info', 'phase_ids'])
            v.append(list(phases.keys()))

            if self.project_dict.macro_running:
                for key, value in zip(k, v):
                    self.project_dict.setItemByPath(key, value)
            else:
                self.project_dict.bulkUpdate(k, v, 'Bulk update of phases')
        self.__last_updated = datetime.now()

    def getPhase(self, phase_name: Union[str, None]) -> Phase:
        """
        Returns a phase from the project dictionary by name if one is supplied. If the phase name is none then all
        phases are returned. If the phase name does not exist KeyError is thrown.

        :param phase_name: Name of the phase to be returned or None for all phases
        :return: Copy of the project dictionaries phase object with name phase_name
        :raises KeyError: The supplied key is not a valid phase name
        """
        if phase_name in self.project_dict['phases']:
            return deepcopy(self.project_dict['phases'][phase_name])
        elif phase_name is None:
            return deepcopy(self.project_dict['phases'])
        else:
            raise KeyError

    @time_it
    def updateExperiments(self):
        experiments = self.calculator.getExperiments()

        if len(self.project_dict['experiments']) == 0:
            self.project_dict.startBulkUpdate('Bulk update of experiments')
            self.project_dict.setItemByPath(['experiments'], experiments)
            self.project_dict.setItemByPath(['info', 'experiment_ids'], list(experiments.keys()))
            self.project_dict.endBulkUpdate()
        else:
            k, v = self.project_dict['experiments'].dictComparison(experiments)

            if not k:
                return
            k = [['experiments', *key] for key in k]

            k.append(['info', 'experiment_ids'])
            v.append(list(experiments.keys()))

            if self.project_dict.macro_running:
                for key, value in zip(k, v):
                    self.project_dict.setItemByPath(key, value)
            else:
                self.project_dict.bulkUpdate(k, v, 'Bulk update of experiments')
        self.__last_updated = datetime.now()

    def getExperiment(self, experiment: Union[str, None]) -> Experiment:
        if experiment in self.project_dict['experiments']:
            return deepcopy(self.project_dict['experiments'][experiment])
        elif experiment is None:
            return deepcopy(self.project_dict['experiments'])
        else:
            raise KeyError

    @time_it
    def updateCalculations(self):
        if self.__last_updated > self.__last_calculated:
            calculations = self.calculator.getCalculations()
            self.project_dict['calculations'] = calculations
            self.__last_calculated = datetime.now()

    def getCalculations(self) -> Calculations:
        self.updateCalculations()
        return self.project_dict['calculations']

    def getCalculation(self, calculation) -> Calculation:
        self.updateCalculations()
        return self.project_dict['calculations'][calculation]

    def setPhase(self, phase: Phase):
        """Set phases (sample model tab in GUI)"""
        if isinstance(phase, Phase):
            new_phase_name = phase['phasename']
            if new_phase_name in self.project_dict['phases'].keys():
                k, v = self.project_dict.getItemByPath(['phases', new_phase_name]).dictComparison(phase)
                k = [['phases', new_phase_name, *ik] for ik in k]
                self._mappedBulkUpdate(self._mappedValueUpdater, k, v)
            else:
                self.addPhase(phase)
            self.__last_updated = datetime.now()
        else:
            raise TypeError

    def setPhases(self, phases: Union[Phase, Phases, None] = None):
        """Set phases (sample model tab in GUI)"""
        if isinstance(phases, Phase):
            new_phase_name = phases['phasename']
            k, v = self.project_dict.getItemByPath(['phases', new_phase_name]).dictComparison(phases)
            k = [['phases', new_phase_name, *ik] for ik in k]
        elif isinstance(phases, Phases):
            k = [['phases', item] for item in list(phases.keys())]
            v = [phases[key] for key in phases.keys()]
        else:
            raise TypeError
        self._mappedBulkUpdate(self._mappedValueUpdater, k, v)
        self.__last_updated = datetime.now()

    def setPhaseRefine(self, phase: str, key: list, value: bool = True):
        if phase not in self.project_dict['phases'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['phases', phase, *key, 'store', 'refine'], value)
        self._mappedRefineUpdater(['phases', phase, *key], value)

    def setPhaseValue(self, phase: str, key: list, value):
        if phase not in self.project_dict['phases'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['phases', phase, *key, 'store', 'value'], value)
        self._mappedValueUpdater(['phases', phase, *key], value)

    def setExperiments(self, experiments: Union[Experiment, Experiments, None] = None):
        """Set experiments (Experimental data tab in GUI)"""
        if isinstance(experiments, Experiment):
            new_exp_name = experiments['name']
            self.project_dict.setItemByPath(['experiments', new_exp_name], experiments)
        elif isinstance(experiments, Experiments):
            self.project_dict.bulkUpdate([['experiments', item] for item in list(experiments.keys())],
                                         [experiments[key] for key in experiments.keys()],
                                         "Setting new experiments")
        self.calculator.setExperiments(self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def setExperimentRefine(self, experiment: str, key: list, value: bool = True):
        if experiment not in self.project_dict['experiments'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['experiments', experiment, *key, 'store', 'refine'], value)
        self._mappedRefineUpdater(['experiments', experiment, *key], value)

    def setExperimentValue(self, experiment: str, key: list, value):
        if experiment not in self.project_dict['experiments'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['experiments', experiment, *key, 'store', 'value'], value)
        self._mappedValueUpdater(['experiments', experiment, *key], value)

    def setCalculatorFromProject(self):
        self.calculator.setObjFromProjectDicts(self.project_dict['phases'], self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def getDictByPath(self, keys: list) -> Any:
        return self.project_dict.getItemByPath(keys)

    def setDictByPath(self, keys: list, value: Any):
        self.project_dict.setItemByPath(keys, value)
        self.setCalculatorFromProject()
        self.updateCalculations()  # IT IS SLOW

    ###
    # Project Information
    ###

    def phasesCount(self) -> int:
        """Returns number of phases in the project."""
        return len(self.project_dict['phases'])

    def experimentsCount(self) -> int:
        """Returns number of experiments in the project."""
        return len(self.project_dict['experiments'])

    def phasesIds(self) -> list:
        """Returns labels of the phases in the project."""
        return list(self.project_dict['phases'].keys())

    def experimentsIds(self) -> list:
        """Returns labels of the experiments in the project."""
        return list(self.project_dict['experiments'].keys())

    def asDict(self) -> dict:
        """Return data dict."""
        project_dict = {}
        try:
            project_dict = self.project_dict.asDict()
        except TypeError:
            self._log.error('Error on copying `project_dict`. It is a python problem')
        return project_dict

    def name(self) -> str:
        return self.project_dict["info"]["name"]

    def asCifDict(self) -> dict:
        """..."""
        return self.calculator.asCifDict()

    ###
    # Refinement
    ###

    def refine(self) -> dict:
        """refinement ..."""
        refinement_res, scipy_refinement_res = self.calculator.refine()

        self.project_dict.startBulkUpdate('Refinement')
        self.setProjectFromCalculator()
        self.project_dict.endBulkUpdate()

        try:
            data = {
                "num_refined_parameters": len(scipy_refinement_res.x),
                "refinement_message": scipy_refinement_res.message,
                "nfev": scipy_refinement_res.nfev,
                "nit": scipy_refinement_res.nit,
                "njev": scipy_refinement_res.njev,
                "final_chi_sq": float(self.final_chi_square)
            }
            return data

        except:
            if scipy_refinement_res is None:
                return {
                    "refinement_message": "No parameters selected for refinement"
                }
            else:
                return {
                    "refinement_message": "Unknown problems during refinement"
                }

    ###
    # Undo/Redo logic
    ###

    def canUndo(self):
        return self.project_dict.canUndo()

    def canRedo(self):
        return self.project_dict.canRedo()

    def clearUndoStack(self):
        self.project_dict.clearUndoStack()

    def undo(self):
        self.project_dict.undo()

    def redo(self):
        self.project_dict.redo()

    ###
    # Hidden internal logic
    ###

    def _mappedBulkUpdate(self, func: Callable, keys: list, values: list):
        self.project_dict.bulkUpdate(keys, values, 'Updating Dictionary')
        for k, v in zip(keys, values):
            if k[-2:] == ['store', 'value']:
                k = k[:-2]
            func(k, v)
        self.__last_updated = datetime.now()
        self.updateCalculations()

    def _mappedValueUpdater(self, key, value):
        update_str = self.project_dict.getItemByPath(key)['mapping']
        self.calculator._mappedValueUpdater(update_str, value)
        self.__last_updated = datetime.now()

    def _mappedRefineUpdater(self, key, value):
        update_str = self.project_dict.getItemByPath(key)['mapping']
        self.calculator._mappedRefineUpdater(update_str, value)

    def setExperiment(self, experiment):
        """Set phases (sample model tab in GUI)"""
        if isinstance(experiment, Experiment):
            new_phase_name = experiment['name']
            if new_phase_name in self.project_dict['experiments'].keys():
                k, v = self.project_dict.getItemByPath(['experiments', new_phase_name]).dictComparison(experiment)
                k = [['experiments', new_phase_name, *ik] for ik in k]
                self._mappedBulkUpdate(self._mappedValueUpdater, k, v)
            else:
                self.addExperiment(experiment)
        else:
            raise TypeError
        self.__last_updated = datetime.now()
