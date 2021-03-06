from typing import Union

import numpy as np
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import LoggedPathDict
from easyInterface import logger as logging


class Limits(LoggedPathDict):
    """
    Generator for limits of a dataset
    """

    def __init__(self, y_obs_lower=-np.Inf, y_obs_upper=np.Inf,
                 y_diff_upper=np.Inf, y_diff_lower=-np.Inf,
                 x_calc=None, y_calc=None):
        if y_calc is None:
            y_calc = [0.0]
        if x_calc is None:
            x_calc = [0.0]
        main = LoggedPathDict(x_min=np.amin(x_calc).item(), x_max=np.amax(x_calc).item(),
                        y_min=(np.amin([np.amin(y_calc), np.amin(y_obs_lower)]).item()),
                        y_max=(np.amax([np.amax(y_calc), np.amax(y_obs_upper)]).item()))

        difference = LoggedPathDict(y_min=np.amin(y_diff_lower).item(),
                              y_max=np.amax(y_diff_upper).item())

        super().__init__(main=main, difference=difference)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Created limits %s', self['main'])


class CrystalBraggPeaks(LoggedPathDict):
    """
    Generator for HKL reflections and corresponding two theta.
    """

    def __init__(self, name: str, h: list, k: list, l: list, ttheta: list):
        super().__init__(name=name, h=h, k=k, l=l, ttheta=ttheta)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Created a bragg peak %s set with %i peaks', name, len(h))
        
    def __repr__(self) -> str:
        return "{} Bragg peaks in phase {}".format(len(self['h']), self['name'])


class BraggPeaks(LoggedPathDict):
    """
    Container for multiple calculations
    """

    def __init__(self, bragg_peaks: Union[CrystalBraggPeaks, dict, list]):
        """
        Constructor for holding multiple bragg peaks
        :param bragg_peaks: A collection of bragg peak dicts
        """
        if isinstance(bragg_peaks, CrystalBraggPeaks):
            bragg_peaks = {
                bragg_peaks['name']: bragg_peaks,
            }
        if isinstance(bragg_peaks, list):
            theseCalculations = dict()
            for bragg_peak in bragg_peaks:
                theseCalculations[bragg_peak['name']] = bragg_peak
            bragg_peaks = theseCalculations
        super().__init__(**bragg_peaks)
        self._log = logging.getLogger(__class__.__module__)

    def __repr__(self) -> str:
        return '{} Calculations'.format(len(self))


class CalculatedPattern(LoggedPathDict):
    """
    Storage container for a calculated pattern
    """
    def __init__(self, x: list, y_diff_lower: list, y_diff_upper: list, y_calc_up: list, y_calc_down: list = [], y_calc_bkg: list = []):
        y_calc_down_temp = y_calc_down
        if len(y_calc_down) == 0:
            y_calc_down_temp = [0]*len(y_calc_up)

        super().__init__(x=x, y_calc_sum=np.array(y_calc_up) + np.array(y_calc_down_temp), y_calc_diff=np.array(y_calc_up) - np.array(y_calc_down_temp),
                         y_calc_up=y_calc_up, y_calc_down=y_calc_down,
                         y_diff_lower=y_diff_lower, y_diff_upper=y_diff_upper,
                         y_calc_bkg=y_calc_bkg)
        self._log = logging.getLogger(__class__.__module__)

    def __repr__(self):
        return 'Pattern of {} points'.format(len(self['x']))


class Calculation(LoggedPathDict):
    """
    Storage container for calculations
    """
    def __init__(self, name: str, bragg_peaks: BraggPeaks, calculated_pattern: CalculatedPattern, limits: Limits):
        super().__init__(name=name, bragg_peaks=bragg_peaks, calculated_pattern=calculated_pattern, limits=limits)
        self._log = logging.getLogger(__class__.__module__)

    @classmethod
    def default(cls, name: str):
        bragg_peaks = BraggPeaks({})
        calculated_pattern = CalculatedPattern([0], [0], [0], [0],[0])
        limits = Limits()
        return cls(name, bragg_peaks, calculated_pattern, limits)

    @classmethod
    def fromPars(cls, name: str, bragg_crystals: CrystalBraggPeaks,
                 y_calc_lower: list, y_calc_upper: list,
                 tth: list, y_calc: list, y_diff_lower: list, y_diff_upper: list, y_calc_bkg: list):
        bragg_peaks = BraggPeaks(bragg_crystals)
        calculated_pattern = CalculatedPattern(tth, y_calc, y_diff_lower, y_diff_upper, y_calc_bkg)
        limits = Limits(y_calc_lower, y_calc_upper, y_diff_upper, y_diff_lower, x_calc=tth, y_calc=y_calc)
        return cls(name, bragg_peaks, calculated_pattern, limits)

    def __repr__(self):
        return 'Pattern [{}] with {} phases'.format(self['name'], len(self['bragg_peaks']))


class Calculations(LoggedPathDict):
    """
    Container for multiple calculations
    """
    def __init__(self, calculations: Union[Calculation, dict, list]):
        """
        Constructor for holding multiple calculations

        :param calculations: A collection of calculation dicts
        """
        if isinstance(calculations, Calculation):
            calculations = {
                calculations['name']: calculations,
            }
        if isinstance(calculations, list):
            theseCalculations = dict()
            for calculation in calculations:
                theseCalculations[calculation['name']] = calculation
            calculations = theseCalculations
        super().__init__(**calculations)
        self._log = logging.getLogger(__class__.__module__)

    def __repr__(self) -> str:
        return '{} Calculations'.format(len(self))
