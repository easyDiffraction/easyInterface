#  Licensed under the GNU General Public License v3.0
#  Copyright (c) of the author (github.com/wardsimon)
#  Created: 26/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import Union, List
from pathlib import Path
import numpy as np


Vector3Like = Union[List[float], np.ndarray]
PathLike = Union[str, Path]
NoneType = type(None)