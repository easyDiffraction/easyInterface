"""
Creating a interface
====================

This demonstrates an example of how to load an example and create a interface to a cryspy calculator. Information about
the project is then displayed.
"""

import os

from easyInterface.Diffraction.Calculators import CryspyCalculator
from easyInterface.Diffraction.Interface import CalculatorInterface


main_rcif = os.path.join('examples', 'Fe3O4_powder-1d_neutrons-pol_5C1(LLB)', 'main.cif')
calculator = CryspyCalculator(main_rcif)

interface = CalculatorInterface(calculator)

print(interface.project_dict)

print(interface.phasesIds())

print(interface.getPhase(interface.phasesIds()[0]))
