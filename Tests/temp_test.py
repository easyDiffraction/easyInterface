import os

from EasyInterface.Calculators import CryspyCalculator
from EasyInterface.Interface import CalculatorInterface


main_rcif = os.path.join('..', 'Examples', 'Fe3O4_powder-1d_neutrons-pol_5C1(LLB)', 'main.cif')
calculator = CryspyCalculator(main_rcif)

interface = CalculatorInterface(calculator)

print(interface.project_dict)

print(interface.phasesIds())

print(interface.getPhase(interface.phasesIds()[0]))
