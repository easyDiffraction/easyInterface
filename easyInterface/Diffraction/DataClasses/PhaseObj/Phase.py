from typing import NoReturn
from .Atom import *
from .SpaceGroup import *
from .Cell import *

from easyInterface import logger as logging


class Phase(PathDict):
    """
    Container for crysolographic phase information
    """
    def __init__(self, name: str, spacegroup: SpaceGroup, cell: Cell, atoms: Union[Atom, dict, Atoms], sites: dict):
        """
        Constructor for a crysolographic phase
        :param name: The name of the crystolographic phase
        :param spacegroup: The phase spacegroup information
        :param cell: The unit cell parameters
        :param atoms: A collection of atoms for the unit cell
        """
        if isinstance(atoms, Atom):
            atoms = {
                atoms['atom_site_label']: atoms,
            }
        atoms = Atoms(atoms)
        super().__init__(phasename=name, spacegroup=spacegroup, cell=cell, atoms=atoms, sites=sites)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('New phase created %s', name)

    @classmethod
    def default(cls, name: str) -> 'Phase':
        """
        Default constructor for a crysolographic phase with a given name
        :return: Default empty phase with a name
        """
        cell = Cell.default()
        spg = SpaceGroup.default()
        atom = {}
        sites = dict(fract_x=[], fract_y=[], fract_z=[], scat_length_neutron=[])
        return cls(name, spacegroup=spg, cell=cell, atoms=atom, sites=sites)

    @classmethod
    def fromPars(cls, name, spacegroup: SpaceGroup, cell: Cell) -> 'Phase':
        atom = {}
        sites = dict(fract_x=[], fract_y=[], fract_z=[], scat_length_neutron=[])
        return cls(name, spacegroup, cell, atom, sites)

    def __str__(self):
        return '{}\n{}\n{}\n'.format(str(self['spacegroup']), str(self['cell']), str(self['atoms']))

    def __repr__(self):
        return 'Phase with {} atoms'.format(len(self['atoms']))


class Phases(PathDict):
    """
    Container for multiple phases
    """
    def __init__(self, phases: Union[Phase, dict, list]):
        """
        Contructor for the phases dict
        :param phases: Collection of phases
        """
        if isinstance(phases, Phase):
            phases = {
                phases['phasename']: phases,
            }
        if isinstance(phases, list):
            thesePhases = dict()
            for phase in phases:
                thesePhases[phase['phasename']] = phase
            phases = thesePhases
        super().__init__(**phases)
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Phases created: %s', self)

    def renamePhase(self, oldPhaseName: str, newPhaseName: str) -> NoReturn:
        """
        Easy method of renaming a phase
        :param oldPhaseName: phase name to be changed
        :param newPhaseName: new phase name
        """
        if oldPhaseName not in self.keys():
            self._log.warning('Key {} not in phases', oldPhaseName)
            raise KeyError
        self[newPhaseName] = self.pop(oldPhaseName)
        self[newPhaseName]['phasename'] = newPhaseName
        self._log.debug('Phasename changed {} -> {}', oldPhaseName, newPhaseName)

    def __repr__(self):
        return '{} Phases'.format(len(self))

