__author__ = 'simonward'
__version__ = "2020_02_01"

import os
from datetime import datetime
from copy import deepcopy
from typing import List, Callable, Any

from easyInterface.Diffraction.DataClasses.DataObj.Calculation import *
from easyInterface.Diffraction.DataClasses.DataObj.Experiment import Experiments, Experiment
from easyInterface.Diffraction.DataClasses.PhaseObj.Phase import Phases, Phase
from easyInterface.Utils.DictTools import UndoableDict
from easyInterface.Diffraction.DataClasses.Utils.InfoObjs import Interface, App, Calculator, Info
from easyInterface.Utils.Helpers import time_it
from easyInterface import logger as logging


class ProjectDict(UndoableDict):
    """
    This class deals with the creation and modification of the main project dictionary
    """

    def __init__(self, interface: Interface, app: App, calculator: Calculator, info: Info, phases: Phases,
                 experiments: Experiments,
                 calculations: Calculations):
        """
        Create the main project dictionary from base classes
        :param app: Details of the EasyDiffraction app
        :param calculator: Details of the Calculator to be used
        :param info: Store of ID's and some fit information
        :param phases: Crystolographic phases in the system
        :param experiments: Experimental data store in the system
        """
        super().__init__(interface=interface, calculator=calculator, app=app, info=info, phases=phases,
                         experiments=experiments, calculations=calculations)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Created a project dictionary')

    @classmethod
    def default(cls) -> 'ProjectDict':
        """
        Create a default and empty project dictionary
        :return: Default project dictionary with undo/redo
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
        Create a main project dictionary from phases and experiments
        :param experiments: A collection of experiments to be compared to calculations
        :param phases: A Collection of crystolographic phases to be calculated
        :return: project dictionary with undo/redo
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
    Interface to calculators in the easyInterface/Diffraction/Calculator folder
    """

    def __init__(self, calculator):
        self._log = logging.getLogger(__class__.__module__)
        self.project_dict = ProjectDict.default()
        self.calculator = calculator
        # Set the calculator info
        CALCULATOR_INFO = self.calculator.calculatorInfo()
        for key in CALCULATOR_INFO.keys():
            self.project_dict['calculator'][key] = CALCULATOR_INFO[key]
        self.__lastupdated = datetime.max
        self.__lastcalculated = datetime.min
        self.setProjectFromCalculator()
        self._log.info("Created: %s", self)

    def __repr__(self) -> str:
        return "easyInterface ({}) with calculator: {} - {}".format(
            self.project_dict['interface']['version'],
            self.project_dict['calculator']['name'],
            self.project_dict['calculator']['version'])

    @property
    def final_chi_square(self) -> float:
        return self.calculator.final_chi_square

    def setProjectFromCalculator(self):
        self.updatePhases()
        self.updateExperiments()
        self.updateCalculations()
        self.project_dict.setItemByPath(['info', 'modified_datetime'],
                                        datetime.fromtimestamp(
                                            os.path.getmtime(self.calculator._main_rcif_path)).strftime(
                                            '%d %b %Y, %H:%M:%S'))
        self.project_dict.setItemByPath(['info', 'name'], self.calculator.getProjectName())
        self.project_dict.setItemByPath(['info', 'refinement_datetime'], str(np.datetime64('now')))

        final_chi_square, n_res = self.calculator.getChiSq()
        final_chi_square = final_chi_square / n_res

        self.project_dict.setItemByPath(['info', 'n_res', 'store', 'value'], n_res)
        self.project_dict.setItemByPath(['info', 'chi_squared', 'store', 'value'], final_chi_square)
        self.__lastupdated = datetime.now()

    ###
    # Setting of Calculator
    ###

    # Phase section
    def setPhaseDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.setPhaseDefinition(exp_path)
        # This will re-create all local directories
        self.updateExperiments()

    def addPhaseDefinition(self, phases_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.addPhaseDefinition(phases_path)
        self.updatePhases()
        # This will notify the GUI models changed
        # self.projectDictChanged.emit()

    def addPhase(self, phase: Phase):
        if phase['phasename'] in self.project_dict['phases'].keys():
            self.setPhase(phase)
        else:
            self.project_dict.setItemByPath(['phases', phase['phasename']], phase)
            self.calculator.addPhase(phase)
        self.__lastupdated = datetime.now()

    def removePhase(self, phase_name):
        self.calculator.removePhaseDefinition(phase_name)
        self.project_dict.rmItemByPath(['phases', phase_name])
        self.__lastupdated = datetime.now()

    # Experiment section
    def setExperimentDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.setExpsDefinition(exp_path)
        # This will re-create all local directories
        self.updateExperiments()

    def addExperimentDefinition(self, phases_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.addExpsDefinition(phases_path)
        self.updateExperiments()

    def addExperiment(self, experiment: Experiment):
        if experiment['name'] in self.project_dict['experiments'].keys():
            self.setExperiment(experiment)
        else:
            self.project_dict.setItemByPath(['experiments', experiment['name']], experiment)
            self.calculator.setExperiments(self.project_dict['experiments'])
        self.__lastupdated = datetime.now()

    def removeExperiment(self, experiment_name):
        self.calculator.removeExpsDefinition(experiment_name)
        self.updateExperiments()
        self.__lastupdated = datetime.now()

    # Output section
    def writeMainCif(self, save_dir: str):
        self.calculator.writeMainCif(save_dir)

    def writePhaseCif(self, save_dir: str):
        self.calculator.writePhaseCif(save_dir)

    def writeExpCif(self, save_dir: str):
        self.calculator.writeExpCif(save_dir)

    def saveCifs(self, save_dir: str):
        self.writeMainCif(save_dir)
        self.writePhaseCif(save_dir)
        self.writeExpCif(save_dir)

    ###
    # Syncing between Calculator/Dict
    ###
    @time_it
    def updatePhases(self):
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
        self.__lastupdated = datetime.now()

    def getPhase(self, phase: Union[str, None]) -> Phase:
        if phase in self.project_dict['phases']:
            return deepcopy(self.project_dict['phases'][phase])
        elif phase is None:
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
        self.__lastupdated = datetime.now()


    def getExperiment(self, experiment: Union[str, None]) -> Experiment:
        if experiment in self.project_dict['experiments']:
            return deepcopy(self.project_dict['experiments'][experiment])
        elif experiment is None:
            return deepcopy(self.project_dict['experiments'])
        else:
            raise KeyError

    @time_it
    def updateCalculations(self):
        if self.__lastupdated > self.__lastcalculated:
            calculations = self.calculator.getCalculations()
            self.project_dict['calculations'] = calculations
            self.__lastcalculated = datetime.now()

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
            self.__lastupdated = datetime.now()
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
        self.__lastupdated = datetime.now()

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
        self.__lastupdated = datetime.now()

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
        self.__lastupdated = datetime.now()

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
        return self.project_dict.asDict()

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
        self.__lastupdated = datetime.now()
        self.updateCalculations()

    def _mappedValueUpdater(self, key, value):
        update_str = self.project_dict.getItemByPath(key)['mapping']
        self.calculator._mappedValueUpdater(update_str, value)
        self.__lastupdated = datetime.now()

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
        self.__lastupdated = datetime.now()
