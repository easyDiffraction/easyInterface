import logging
import os
from datetime import datetime
from copy import deepcopy
from typing import List

from easyInterface.DataClasses.DataObj.Calculation import *
from easyInterface.DataClasses.DataObj.Experiment import *
from easyInterface.DataClasses.PhaseObj.Phase import *
from easyInterface.DataClasses.Utils.DictTools import UndoableDict
from easyInterface.DataClasses.Utils.InfoObjs import App, Calculator, Info


class ProjectDict(UndoableDict):
    """
    This class deals with the creation and modification of the main project dictionary
    """

    def __init__(self, app: App, calculator: Calculator, info: Info, phases: Phases, experiments: Experiments,
                 calculations: Calculations):
        """
        Create the main project dictionary from base classes
        :param app: Details of the EasyDiffraction app
        :param calculator: Details of the Calculator to be used
        :param info: Store of ID's and some fit information
        :param phases: Crystolographic phases in the system
        :param experiments: Experimental data store in the system
        """
        super().__init__(app=app, calculator=calculator, info=info, phases=phases, experiments=experiments,
                         calculations=calculations)

    @classmethod
    def default(cls) -> 'ProjectDict':
        """
        Create a default and empty project dictionary
        :return: Default project dictionary with undo/redo
        """
        app = App.default()
        info = Info.default()
        calculator = Calculator.default()
        phases = Phases({})
        experiments = Experiments({})
        calculations = Calculations({})
        return cls(app, calculator, info, phases, experiments, calculations)

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
        if not isinstance(experiments, Experiments):
            experiments = Experiments(experiments)
        if not isinstance(phases, Phases):
            phases = Phases(phases)
        if not isinstance(calculations, Calculations):
            calculations = Calculations(calculations)
        return cls(app, calculator, info, phases, experiments, calculations)


class CalculatorInterface:
    def __init__(self, calculator):
        logging.info("---")
        self.project_dict = ProjectDict.default()
        self.calculator = calculator
        logging.info("self.calculator:")
        logging.info(type(self.calculator))
        logging.info(self.calculator)
        self.setProjectFromCalculator()

        # Set the calculator info
        # TODO this should be a non-logged update
        CALCULATOR_INFO = self.calculator.calculatorInfo()
        for key in CALCULATOR_INFO.keys():
            self.project_dict.setItemByPath(['calculator', key], CALCULATOR_INFO[key])

    # projectDictChanged = Signal()

    def __repr__(self) -> str:
        return "easyInterface with calculator: {} - {}".format(
            self.project_dict['calculator']['name'],
            self.project_dict['calculator']['version'])

    def setProjectFromCalculator(self):
        # TODO initiate buld update here
        self.updatePhases()
        self.updateExperiments()
        self.updateCalculations()
        self.project_dict.setItemByPath(['info', 'modified_datetime'],
                                        datetime.fromtimestamp(
                                            os.path.getmtime(self.calculator._main_rcif_path)).strftime(
                                            '%d %b %Y, %H:%M:%S'))
        self.project_dict.setItemByPath(['info', 'refinement_datetime'], str(np.datetime64('now')))

        final_chi_square, n_res = self.calculator.getChiSq()
        final_chi_square = final_chi_square / n_res

        self.project_dict.setItemByPath(['info', 'n_res', 'store', 'value'], n_res)
        self.project_dict.setItemByPath(['info', 'chi_squared', 'store', 'value'], final_chi_square)

        # self.projectDictChanged.emit()

    #
    def updateExpsDefinition(self, exp_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.updateExpsDefinition(exp_path)
        # This will re-create all local directories
        self.updateExperiments()

    def updatePhaseDefinition(self, phases_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        self.calculator.updatePhaseDefinition(phases_path)
        self.updatePhases()

        # This will notify the GUI models changed
        # self.projectDictChanged.emit()

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

    def updatePhases(self):
        phases = self.calculator.getPhases()

        # for key, val in phases.items():
        #    logging.info(key)
        #    logging.info(dict(val))

        k, v = self.project_dict['phases'].dictComparison(phases)

        if not k:
            return

        k = [['phases', *key] for key in k]

        k.append(['info', 'phase_ids'])
        v.append(list(phases.keys()))

        self.project_dict.bulkUpdate(k, v, 'Bulk update of phases')

    def updateExperiments(self):
        experiments = self.calculator.getExperiments()

        k, v = self.project_dict['experiments'].dictComparison(experiments)

        if not k:
            return
        k = [['experiments', *key] for key in k]

        k.append(['info', 'experiment_ids'])
        v.append(list(experiments.keys()))

        self.project_dict.bulkUpdate(k, v, 'Bulk update of experiments')

    def getCalculations(self):
        self.updateCalculations()
        return self.project_dict['calculations']

    def updateCalculations(self):
        calculations = self.calculator.getCalculations()
        self.project_dict.setItemByPath(['calculations'], calculations)

    def getPhase(self, phase) -> Phase:
        if phase in self.project_dict['phases']:
            return deepcopy(self.project_dict['phases'][phase])
        else:
            raise KeyError

    def getExperiment(self, experiment):
        if experiment in self.project_dict['experiments']:
            return deepcopy(self.project_dict['experiments'][experiment])
        else:
            raise KeyError

    def setPhases(self, phases=None):
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

    def setExperiments(self, experiments=None):
        """Set experiments (Experimental data tab in GUI)"""
        if isinstance(experiments, Experiment):
            new_exp_name = experiments['name']
            self.project_dict.setItemByPath(['experiments', new_exp_name], experiments)
        elif isinstance(experiments, Experiments):
            self.project_dict.bulkUpdate([['experiments', item] for item in list(experiments.keys())],
                                         [experiments[key] for key in experiments.keys()],
                                         "Setting new experiments")
        self.calculator.setExperiments(self.project_dict['experiments'])

    def setCalculatorFromProject(self):
        self.calculator.setObjFromProjectDicts(self.project_dict['phases'], self.project_dict['experiments'])

    def getDictByPath(self, keys: list):
        return self.project_dict.getItemByPath(keys)

    def setDictByPath(self, keys: list, value):
        self.project_dict.setItemByPath(keys, value)
        self.setCalculatorFromProject()
        self.updateCalculations()  # IT IS SLOW
        # self.projectDictChanged.emit()

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

    def refine(self):
        """refinement ..."""
        refinement_res, scipy_refinement_res = self.calculator.refine()

        self.setProjectFromCalculator()

        try:
            return {
                "num_refined_parameters": len(scipy_refinement_res.x),
                "refinement_message": scipy_refinement_res.message,
                "nfev": scipy_refinement_res.nfev,
                "nit": scipy_refinement_res.nit,
                "njev": scipy_refinement_res.njev,
                "final_chi_sq": float(self.final_chi_square)
            }
        except:
            if scipy_refinement_res is None:
                return {
                    "refinement_message": "No parameters selected for refinement"
                }
            else:
                return {
                    "refinement_message": "Unknown problems during refinement"
                }

    @property
    def final_chi_square(self) -> float:
        return self.calculator.final_chi_square

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

    def _mappedBulkUpdate(self, func: Callable, keys: list, values:list):
        self.project_dict.bulkUpdate(keys, values, 'Updating Dictionary')
        for k, v in zip(keys, values):
            if k[-2:] == ['store', 'value']:
                k = k[:-2]
            func(k, v)
        self.updateCalculations()

    def _mappedValueUpdater(self, key, value):
        update_str = self.project_dict.getItemByPath(key)['mapping']
        self.calculator._mappedValueUpdater(update_str, value)

    def _mappedRefineUpdater(self, key, value):
        update_str = self.project_dict.getItemByPath(key)['mapping']
        self.calculator._mappedRefineUpdater(update_str, value)
