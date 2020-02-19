"""
Creating a QT interface
=======================

This demonstrates an example of how to load an example and create a QT interface to a cryspy calculator. Information
about the project is then displayed.
"""

import os

from easyInterface.Utils.Helpers import getExamplesDir
from easyInterface.Diffraction.Calculators import CryspyCalculator
from easyInterface.Diffraction.QtInterface import QtCalculatorInterface

data_dir = getExamplesDir()
main_rcif = os.path.join(data_dir, 'Fe3O4_powder-1d_neutrons-pol_5C1(LLB)', 'main.cif')
calculator = CryspyCalculator(main_rcif)

interface = QtCalculatorInterface(calculator, None)

print(interface.project_dict)

print(interface.phasesIds())

print(interface.getPhase(interface.phasesIds()[0]))
