#  Licensed under the GNU General Public License v3.0
#  Copyright (c) of the author (github.com/wardsimon)
#  Created: 25/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import json
import re

with open('easyInterface/Common/periodic_table.json', "r") as f:
    _pt_data = json.load(f)

with open('easyInterface/Utils/scattering_lengths.json', 'r') as R:
    sl = json.loads(R.read())

for atom in _pt_data.keys():
    r = re.compile("([0-9]+){}$".format(atom))
    isotopes = [reg.group(1) for reg in [r.match(item) for item in sl.keys()] if reg is not None]
    _pt_data[atom]['N Scattering Lengths'] = {}

    for isotope in isotopes:
        key = isotope + atom
        _pt_data[atom]['N Scattering Lengths'][key] = sl[key]

data = json.dumps(_pt_data, indent='\t')
with open('easyInterface/Common/PT_WSL.json', 'w') as W:
    W.write(data)