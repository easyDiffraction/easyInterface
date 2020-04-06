__author__ = 'simonward'
__version__ = "2020_03_09"

import os
from datetime import datetime
from copy import deepcopy
from typing import List, Callable, Any, Union, Optional, NoReturn

from easyInterface.Diffraction.DataClasses.DataObj.Calculation import Calculation, Calculations
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import Experiments, Experiment, ExperimentPhase
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases, Phase
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import LoggedUndoableDict
from easyInterface.Diffraction.DataClasses.Utils.InfoObjs import Interface, App, Calculator, Info
from easyInterface.Utils.Helpers import time_it
from easyInterface import logger as logging

from numpy import datetime64


class ProjectDict(LoggedUndoableDict):
    """
    This class deals with the creation and modification of the main project dictionary.
    """

    def __init__(self, interface: Interface, app: App, calculator: Calculator, info: Info, phases: Phases,
                 experiments: Experiments, calculations: Calculations) -> None:
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
                 calculations: Optional[Union[Calculations, Calculation, List[Calculation]]] = {}) -> 'ProjectDict':
        """
        Create a main project dictionary from phases and experiments.

        :param calculations:
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

    def __init__(self, calculator: 'easyInterface.Diffraction.Calculator') -> None:
        """
        Initialise an interface with a `calculator` of the `easyInterface.Diffraction.Calculator` class.

        :param calculator: Calculator of the `easyInterface.Diffraction.Calculator` class.
        """

        self._log: logging.logger = logging.getLogger(__class__.__module__)
        self.project_dict: ProjectDict = ProjectDict.default()
        self.calculator = calculator
        # Set the calculator info
        CALCULATOR_INFO = self.calculator.calculatorInfo()
        for key in CALCULATOR_INFO.keys():
            self.project_dict['calculator'][key] = CALCULATOR_INFO[key]
        self.__last_updated: datetime = datetime.max
        self.__last_calculated: datetime = datetime.min
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

    def setProjectFromCalculator(self) -> NoReturn:
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
    def setPhaseDefinition(self, phase_path: str) -> NoReturn:
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

    def addPhaseDefinition(self, phase_path: str) -> NoReturn:
        """
        Add new phases from a cif file to the list of existing crystal phases in the calculator.

        :param phase_path: Path to a phase definition file (`.cif`)

        Example::

            interface = CalculatorInterface(calculator)
            phase_path = '~/Experiments/new_phase.cif'
            interface.addPhaseDefinition(phase_path)
        """
        self.calculator.addPhaseDefinition(phase_path)
        self.updatePhases()

    def addPhase(self, phase: Phase) -> NoReturn:
        """
        Add a new phase from an easyInterface phase object to the list of existing crystal phases in the calculator.

        :param phase: New phase to be added to the phase list.
        """
        if phase['phasename'] in self.project_dict['phases'].keys():
            self.setPhase(phase)
        else:
            self.project_dict.setItemByPath(['phases', phase['phasename']], phase)
            self.calculator.addPhase(phase)
        self.__last_updated = datetime.now()

    def removePhase(self, phase_name: str) -> NoReturn:
        """
        Remove a phase of a given name from the dictionary and the calculator object.

        :param phase_name: name of the phase to be removed.
        """
        self.calculator.removePhaseDefinition(phase_name)
        self.project_dict.rmItemByPath(['phases', phase_name])
        self.__last_updated = datetime.now()

    def addPhaseToExp(self, exp_name: str, phase_name: str, scale: float = 0.0, field: float = 0.0) -> NoReturn:
        """
        Link a phase in the project dictionary to an experiment in the project dictionary. Links in the calculator will
        also be made.

        :param exp_name: The name of the experiment
        :param phase_name: The name of the phase to be associated with the experiment
        :param scale: The scale of the crystallographic phase in the experimental system.
        :raises KeyError: If the exp_name or phase_name are unknown
        """
        self.calculator.associatePhaseToExp(exp_name, phase_name, scale)
        currentPhases = self.project_dict.getItemByPath(['experiments', 'phase'])
        newPhase = ExperimentPhase.fromPars(phase_name, scale, field)
        if currentPhases is None:
            currentPhases = {phase_name: newPhase}
        else:
            currentPhases[phase_name] = newPhase
        self.project_dict.setItemByPath(['experiments', exp_name, 'phase'], currentPhases)
        self.__last_updated = datetime.now()

    def removePhaseFromExp(self, exp_name: str, phase_name: str) -> NoReturn:
        """
        Remove the link between an experiment and a crystallographic phase. Links in the calculator will also be removed.

        :param exp_name: The name of the experiment.
        :param phase_name: The name of the phase to be removed.
        :raises KeyError: If the exp_name or phase_name are unknown
        """
        self.calculator.disassociatePhaseFromExp(exp_name, phase_name)
        self.project_dict.rmItemByPath(['experiments', exp_name, 'phase', phase_name])
        self.__last_updated = datetime.now()

    # Experiment section
    def setExperimentDefinition(self, exp_path: str) -> NoReturn:
        """
        Set an experiment/s to be simulated from a cif file. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_path: Path to a experiment file (`.cif`)
        """
        self.calculator.setExpsDefinition(exp_path)
        # This will re-create all local directories
        self.updateExperiments()

    def setExperimentDefinitionFromString(self, exp_cif_string: str) -> NoReturn:
        """
        Set an experiment/s to be simulated from a string. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_cif_string: String containing the contents of an experiment file (`.cif`)
        """
        self.calculator.addExpDefinitionFromString(exp_cif_string)
        # This will re-create all local directories
        self.updateExperiments()

    def addExperimentDefinition(self, exp_path: str) -> NoReturn:
        """
        Add an experiment to be simulated from a cif file. Note that this will not have any crystallographic phases
        associated with it.

        :param exp_path: Path to a experiment file (`.cif`)
        """
        self.calculator.addExpsDefinition(exp_path)
        self.updateExperiments()

    def addExperiment(self, experiment: Experiment) -> NoReturn:
        """
        Add an experiment to the list of experiments in both the project dict and the calculator.

        :param experiment: Experiment object to be added to the system.
        """
        if experiment['name'] in self.project_dict['experiments'].keys():
            self.setExperiment(experiment)
        else:
            self.project_dict.setItemByPath(['experiments', experiment['name']], experiment)
            self.calculator.setExperiments(self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def removeExperiment(self, experiment_name: str) -> NoReturn:
        """
        Remove a experiment from both the project dictionary and the calculator.

        :param experiment_name: Name of the experiment to be removed.
        """
        self.calculator.removeExpsDefinition(experiment_name)
        self.updateExperiments()
        self.__last_updated = datetime.now()

    # Output section
    def writeMainCif(self, save_dir: str) -> NoReturn:
        """
        Write the `main.cif` where links to the experiments and phases are stored and other generalised project
        information.

        :param save_dir: Directory to where the main cif file should be saved.
        """
        self.calculator.writeMainCif(save_dir)

    def writePhaseCif(self, save_dir: str) -> NoReturn:
        """
        Write the `phases.cif` where all phases in the project dictionary are saved to file. This cif file should be
        compatible with other crystallographic software.

        :param save_dir: Directory to where the phases cif file should be saved.
        """
        self.calculator.writePhaseCif(save_dir)

    def writeExpCif(self, save_dir: str) -> NoReturn:
        """
        Write the `experiments.cif` where all experiments in the project dictionary are saved to file. This includes the
        instrumental parameters and which phases are in the experiment/s

        :param save_dir: Directory to where the experiment cif file should be saved.
        """
        self.calculator.writeExpCif(save_dir)

    def saveCifs(self, save_dir: str) -> NoReturn:
        """
        Write project cif files (`main.cif`, `experiments.cif` and `phases.cif`) to a user supplied directory. This
        contains all information needed to recreate the project dictionary.

        :param save_dir: Directory to where the project cif files should be saved.
        """
        self.writeMainCif(save_dir)
        self.writePhaseCif(save_dir)
        self.writeExpCif(save_dir)

    ###
    # Syncing between Calculator/Dict
    ###
    @time_it
    def updatePhases(self) -> NoReturn:
        """
        Synchronise the phases in project dictionary by queering the calculator object.
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
        Returns a phase from the project dictionary by name if one is supplied. If the phase name is None then all
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
    def updateExperiments(self) -> NoReturn:
        """
        Synchronise the experiments portion of the project dictionary from the calculator.
        """
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

    def getExperiment(self, experiment_name: Union[str, None]) -> Experiment:
        """
        Returns a experiment from the project dictionary by name if one is supplied. If the experiment name is None then
        all experiments are returned. If the experiment name does not exist KeyError is thrown.

        :param experiment_name: Name of the experiment to be returned or None for all experiments
        :return: Copy of the project dictionaries phase object with name experiment_name
        :raises KeyError: The supplied key is not a valid experiment name
        """
        if experiment_name in self.project_dict['experiments']:
            return deepcopy(self.project_dict['experiments'][experiment_name])
        elif experiment_name is None:
            return deepcopy(self.project_dict['experiments'])
        else:
            raise KeyError

    @time_it
    def updateCalculations(self) -> NoReturn:
        """
        Calculate all experiments and populate the calculations field in the project dictionary. Note that this will
        only occur if a member of the phases or experiments section of the project dictionary has been modified since
        the last call to `updateCalculations`.
        """
        if self.__last_updated > self.__last_calculated:
            calculations = self.calculator.getCalculations()
            self.project_dict['calculations'] = calculations
            self.__last_calculated = datetime.now()

    def getCalculations(self) -> Calculations:
        """
        Returns all calculations in the project dictionary. Calculations will be updated if members of the phases or
        experiments section of the project dictionary has been modified.

        :return: Calculations object containing all calculations.
        """
        self.updateCalculations()
        return self.project_dict['calculations']

    def getCalculation(self, calculation_name: str) -> Calculation:
        """
        Returns a specified calculation from the project dictionary.

        :param calculation_name: Name of the calculation to be returned.
        :raises KeyError: If the calculation_name is not known.
        :return: Calculation requested.
        """
        self.updateCalculations()
        calculation = self.project_dict['calculations'][calculation_name]
        return calculation

    def setPhase(self, phase: Phase) -> NoReturn:
        """
        Modify a phase in the calculator. The phase will be added if it does not currently exist.

        :param phase: easyInterface phase object to be added.
        :raises TypeError: If the phase object is not a easyInterface phase object.
        """
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

    def setPhases(self, phases: Union[Phase, Phases]) -> NoReturn:
        """
        Set the phases in the calculator to an easyInterface phases object. If a phase in the supplied phases exists
        then the phase will be modified, if not, it will be added.

        :param phases: phases to be added to the calculator.
        :raises TypeError: If the phase object is not a easyInterface phase/phases object or dictionary object.
        """
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

    def setPhaseRefine(self, phase: str, key: List[str], value: bool = True) -> NoReturn:
        """
        Shortcut for setting the refinement key for items in the phase list.

        :param phase: Name of phase to be modified
        :param key: Location of element to be modified in the named phase.
        :param value: Should the parameter specified by above be refined

        :raises KeyError: If phase is unknown
        """
        if phase not in self.project_dict['phases'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['phases', phase, *key, 'store', 'refine'], value)
        self._mappedRefineUpdater(['phases', phase, *key], value)

    def setPhaseValue(self, phase: str, key: List[str], value) -> NoReturn:
        """
        Shortcut for setting the value key for items in the phase list.

        :param phase: Name of phase to be modified
        :param key: Location of element to be modified in the named phase.
        :param value: New value of the parameter specified by above

        :raises KeyError: If phase is unknown
        """
        if phase not in self.project_dict['phases'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['phases', phase, *key, 'store', 'value'], value)
        self._mappedValueUpdater(['phases', phase, *key], value)

    def setExperiment(self, experiment: Experiment) -> NoReturn:
        """
        Set an experiment to the project dictionary. If an experiment by the same name exists, the necessary changes will
        be propagated. If if does not exist, then it will be added to the project dictionary.

        :param experiment: Experiment container with experimental information
        :raises TypeError: If the input isn't an `Experiment`.
        """
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

    def setExperiments(self, experiments: Union[Experiment, Experiments]):
        """
        Overwrite all experiments in the project dictionary with supplied experiments.

        :param experiments: Experiments container with experimental information
        :raises TypeError: If the input isn't an `Experiments` or `Experiment.
        """
        if isinstance(experiments, Experiment):
            new_exp_name = experiments['name']
            self.project_dict.setItemByPath(['experiments', new_exp_name], experiments)
        elif isinstance(experiments, Experiments):
            self.project_dict.bulkUpdate([['experiments', item] for item in list(experiments.keys())],
                                         [experiments[key] for key in experiments.keys()],
                                         "Setting new experiments")
        else:
            raise TypeError
        self.calculator.setExperiments(self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def setExperimentRefine(self, experiment: str, key: List[str], value: bool = True) -> NoReturn:
        """
        Shortcut for setting the refinement key for items in the experiment list.

        :param experiment: Name of experiment to be modified
        :param key: Location of element to be modified in the named experiment.
        :param value: Should the parameter specified by above be refined

        :raises KeyError: If experiment is unknown
        """
        if experiment not in self.project_dict['experiments'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['experiments', experiment, *key, 'store', 'refine'], value)
        self._mappedRefineUpdater(['experiments', experiment, *key], value)

    def setExperimentValue(self, experiment: str, key: List[str], value):
        """
        Shortcut for setting the value key for items in the experiment list.

        :param experiment: Name of experiment to be modified
        :param key: Location of element to be modified in the named experiment.
        :param value: New value of the parameter specified by above

        :raises KeyError: If experiment is unknown
        """
        if experiment not in self.project_dict['experiments'].keys():
            raise KeyError
        if key[-2:] == ['store', 'value']:
            key = key[:-2]
        self.project_dict.setItemByPath(['experiments', experiment, *key, 'store', 'value'], value)
        self._mappedValueUpdater(['experiments', experiment, *key], value)

    def setCalculatorFromProject(self) -> NoReturn:
        """
        Resets the project phases and experiments fields of the project dictionary from the calculator.
        """
        self.calculator.setObjFromProjectDicts(self.project_dict['phases'], self.project_dict['experiments'])
        self.__last_updated = datetime.now()

    def getDictByPath(self, keys: List[str]) -> Any:
        """
        Returns an object in the project dictionary by the path to the object.

        :param keys: Path to the object in the project dictionary
        :return: Object from the project dictionary.

        :raises KeyError: The supplied keys do not return an object in the project dictionary
        """
        return self.project_dict.getItemByPath(keys)

    def setDictByPath(self, keys: List[str], value: Any) -> NoReturn:
        """
        Set an object in the project dictionary by a key path.

        :param keys: Path to the object to be modified/created
        :param value: Value to be set at the key path
        """
        self.project_dict.setItemByPath(keys, value)
        self.setCalculatorFromProject()
        self.updateCalculations()  # IT IS SLOW

    ###
    # Project Information
    ###

    def phasesCount(self) -> int:
        """
        Get the number of phases in the project dictionary.

        :return: number of phases in the project dictionary.
        """
        return len(self.project_dict['phases'])

    def experimentsCount(self) -> int:
        """
        Get the number of experiments in the project dictionary.

        :return: number of experiments in the project dictionary.
        """
        return len(self.project_dict['experiments'])

    def phasesIds(self) -> List[str]:
        """
        Get the labels of the phases in the project dictionary.

        :return: labels of the phases in the project dictionary.
        """
        return list(self.project_dict['phases'].keys())

    def experimentsIds(self) -> List[str]:
        """
        Returns labels of the experiments in the project dictionary.
        """
        return list(self.project_dict['experiments'].keys())

    def asDict(self) -> dict:
        """
        Converts the project dictionary info a standard python dictionary. If there is an error then an empty dictionary
        is returned.

        :return: Python dictionary of the project dictionary.
        """
        project_dict = {}
        try:
            project_dict = self.project_dict.asDict()
        except TypeError:
            self._log.error('Error on copying `project_dict`. It is a python problem')
        return project_dict

    def name(self) -> str:
        """
        Returns the name of  the current project.

        :return: Name of the current project
        """
        return self.project_dict["info"]["name"]

    def asCifDict(self) -> str:
        """
        Converts the project dictionary into a `cif` structure.

        :return: Project dictionary as a string encoded to the cif specification.
        """
        return self.calculator.asCifDict()

    ###
    # Refinement
    ###

    def refine(self) -> dict:
        """
        Perform a refinement on parameters which are marked in the project dictionary. If the refinement fails then only
        the "refinement_message" will be returned in the results dictionary with an explanation of the error.

        :return: Refinement results of the following fields: "num_refined_parameters", "refinement_message",
                "nfev", "nit", "njev", "final_chi_sq"
        """
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

    def canUndo(self) -> bool:
        """
        Informs on if the project dictionary can have undo() called.

        :return: Can or Can't undo the project dictionary.
        """
        return self.project_dict.canUndo()

    def canRedo(self) -> bool:
        """
        Informs on if the project dictionary can have redo() called. Typically called after an undo function call.

        :return: Can or Can't redo the project dictionary.
        """
        return self.project_dict.canRedo()

    def clearUndoStack(self) -> NoReturn:
        """
        Resets the Undo/Redo stack of the project dictionary.

        ALL PREVIOUS UNDO/REDO EDITS WILL BE LOST
        """
        self.project_dict.clearUndoStack()

    def undo(self) -> NoReturn:
        """
        Perform an undo operation on the project dictionary.
        """
        self.project_dict.undo()

    def redo(self) -> NoReturn:
        """
        Perform an redo operation on the project dictionary.
        """
        self.project_dict.redo()

    ###
    # Hidden internal logic
    ###

    def _mappedBulkUpdate(self, func: Callable, keys: List[List], values: List[Any]) -> NoReturn:
        """
        Perform a bulk update on the project dictionary

        :param func: An updater function which can take key (list) and value pairs and update the project dictionary
        :param keys: List of update keys, each consisting of a list representing an update key
        :param values: List of values to be set.
        """
        self.project_dict.bulkUpdate(keys, values, 'Updating Dictionary')
        for k, v in zip(keys, values):
            if k[-2:] == ['store', 'value']:
                k = k[:-2]
            func(k, v)
        self.__last_updated = datetime.now()
        self.updateCalculations()

    def _mappedValueUpdater(self, key: list, value: Any) -> NoReturn:
        """
        Updater function for `_mappedBulkUpdate`. This function modifies values

        :param key: Location of update
        :param value: Update value
        """

        def code_error(keys):
            if keys[0] == 'phases':
                self.updatePhases()
            else:
                self.updateExperiments()
            self.setCalculatorFromProject()
            self.__last_updated = datetime.now()
        try:
            update_str = self.project_dict.getItemByPath(key)['mapping']
            try:
                self.calculator._mappedValueUpdater(update_str, value)
            except TypeError:
                code_error(key)
        except (KeyError, TypeError):
            code_error(key)
        self.__last_updated = datetime.now()

    def _mappedRefineUpdater(self, key: list, value: bool) -> NoReturn:
        """
        Updater function for `_mappedBulkUpdate`. This function modifies refinement

        :param key: Location of update
        :param value: Update value
        """

        def code_error(keys):
            if keys[0] == 'phases':
                self.updatePhases()
            else:
                self.updateExperiments()
            self.setCalculatorFromProject()
            self.__last_updated = datetime.now()
        try:
            update_str = self.project_dict.getItemByPath(key)['mapping']
            try:
                self.calculator._mappedRefineUpdater(update_str, value)
            except TypeError:
                code_error(key)
        except (KeyError, TypeError):
            code_error(key)
