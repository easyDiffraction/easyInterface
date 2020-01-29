import logging

from easyInterface.Interface import *
from PySide2.QtCore import QObject, Signal, Slot


class QtCalculatorInterface(CalculatorInterface, QObject):
    def __init__(self, calculator, parent=None):
        QObject.__init__(self, parent)
        CalculatorInterface.__init__(self, calculator)

    projectDictChanged = Signal()
    canUndoOrRedoChanged = Signal()

    @Slot(result=bool)
    def canUndo(self):
        return CalculatorInterface.canUndo(self)

    @Slot(result=bool)
    def canRedo(self):
        return CalculatorInterface.canRedo(self)

    @Slot()
    def clearUndoStack(self):
        CalculatorInterface.clearUndoStack(self)

    @Slot()
    def undo(self):
        CalculatorInterface.undo(self)
        self.setCalculatorFromProject()
        self.projectDictChanged.emit()

    @Slot()
    def redo(self):
        CalculatorInterface.redo(self)
        self.setCalculatorFromProject()
        self.projectDictChanged.emit()

    def __repr__(self) -> str:
        return "easyDiffraction QT interface with calculator: {} - {}".format(
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

    def refine(self) -> dict:
        """refinement ..."""
        refinement_res = CalculatorInterface.refine(self)
        self.projectDictChanged.emit()
        return refinement_res

