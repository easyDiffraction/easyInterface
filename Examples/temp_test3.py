import os

from easyInterface import logger, logging
logger.setLevel(logging.DEBUG)
logger.addSysOutput()
logger.addNameFilter('easyInterface.Diffraction.Calculators')

from easyInterface.Diffraction.Calculators import CryspyCalculator
from easyInterface.Diffraction.Interface import CalculatorInterface


main_rcif = os.path.join('Examples', 'PbSO4_powder-1d_neutrons-unpol_D1A(ILL)', 'main.cif')
calculator = CryspyCalculator(main_rcif)

interface = CalculatorInterface(calculator)

print(interface.project_dict)

phase_ids = interface.phasesIds()

print(phase_ids)

phase = interface.getPhase(phase_ids[0])
phase['phasename'] = 'PbSO5'
interface.addPhase(phase)
interface.removePhase('PbSO5')

phase = interface.getPhase(phase_ids[0])
interface.setPhaseValue(phase_ids[0], ['atoms', 'Pb', 'fract_x'], 0.18)
interface.setPhases(phase)
print(phase)

interface.setPhaseRefine(phase_ids[0], ['atoms', 'Pb', 'fract_x'], True)


calc = interface.getCalculations()
print(calc)

res = interface.refine()

print(res)
