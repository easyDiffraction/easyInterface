from EasyInterface.Interface import *
from PySide2.QtCore import QObject, Signal


class QtCalculatorInterface(CalculatorInterface, QObject):
    def __init__(self, calculator, parent=None):
        super(QObject, self).__init__(parent)
        super(CalculatorInterface, self).__init__(calculator)

    projectDictChanged = Signal()

    def __repr__(self) -> str:
        return "EasyDiffraction QT interface with calculator: {} - {}".format(
            self.project_dict['calculator']['name'],
            self.project_dict['calculator']['version'])

    def setProjectFromCalculator(self):
        #TODO initiate buld update here
        CalculatorInterface.setProjectFromCalculator(self)
        self.projectDictChanged.emit()

    def updatePhaseDefinition(self, phases_path: str):
        """
        Parse the relevant phases file and update the corresponding model
        """
        CalculatorInterface.updatePhaseDefinition(self)
        self.projectDictChanged.emit()

    def updatePhases(self, emit: bool = True):
        CalculatorInterface.updatePhases(self)

        # This will notify the GUI models changed
        if emit:
            self.projectDictChanged.emit()

    def updateExperiments(self, emit: bool = True):
        CalculatorInterface.updateExperiments(self)
        # This will notify the GUI models changed
        if emit:
            self.projectDictChanged.emit()

    def updateCalculations(self, emit: bool = True):
        CalculatorInterface.updateCalculations(self)
        # This will notify the GUI models changed
        if emit:
            self.projectDictChanged.emit()

    def setDictByPath(self, keys: list, value):
        CalculatorInterface.setDictByPath(self, keys, value)
        self.projectDictChanged.emit()

    def refine(self):
        """refinement ..."""
        refinement_res, scipy_refinement_res = CalculatorInterface.refine(self)
        self.projectDictChanged.emit()
        return refinement_res, scipy_refinement_res

