from typing import NoReturn
from .Atom import *
from .SpaceGroup import *
from .Cell import *

from easyInterface import logger as logging
from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import ContainerObj, LoggedPathDict


class Phase(LoggedPathDict):
    """
    Container for crystallographic phase information
    """
    def __init__(self, name: str, spacegroup: SpaceGroup, cell: Cell, atoms: Union[Atom, dict, Atoms], sites: dict):
        """
        Constructor for a crystallographic phase

        :param name: The name of the crystallographic phase
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
        Default constructor for a crystallographic phase with a given name

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


class Phases(ContainerObj):
    """
    Container for multiple phases
    """
    def __init__(self, phases: Union[Phase, dict, list]):
        """
        Constructor for the phases dict

        :param phases: Collection of phases
        """
        super().__init__(phases, Phase, 'phasename')
        self._log = logging.getLogger(__class__.__module__)
        self._log.debug('Phases created: %s', self)

    def renamePhase(self, old_phase_name: str, new_phase_name: str) -> NoReturn:
        """
        Easy method of renaming a phase

        :param old_phase_name: phase name to be changed
        :param new_phase_name: new phase name
        """
        if old_phase_name not in self.keys():
            self._log.warning('Key {} not in phases', old_phase_name)
            raise KeyError
        self[new_phase_name] = self.pop(old_phase_name)
        self[new_phase_name]['phasename'] = new_phase_name
        self._log.debug('Phasename changed {} -> {}'.format(old_phase_name, new_phase_name))

    def __repr__(self):
        return '{} Phases'.format(len(self))

