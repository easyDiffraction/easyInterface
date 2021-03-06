from ..Utils.BaseClasses import Base, LoggedPathDict
from easyInterface import logger as logging

SG_DETAILS = {
    'crystal_system': {
        'header': 'Crystal system',
        'tooltip': 'The name of the system of geometric crystal classes of space groups (crystal system) to which the space group belongs.',
        'url': 'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Ispace_group_crystal_system.html',
        'default': ('', '')
    },
    'space_group_name_HM_ref': {
        'header': 'Symbol',
        'tooltip': 'The short international Hermann-Mauguin space-group symbol.',
        'url': 'https://www.iucr.org/__data/iucr/cifdic_html/2/cif_sym.dic/Ispace_group.name_H-M_ref.html',
        'default': ('', '')
    },
    'space_group_IT_number': {
        'header': 'Number',
        'tooltip': 'The number as assigned in International Tables for Crystallography Vol. A.',
        'url': 'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Ispace_group_crystal_system.html',
        'default': (0, '')
    },
    'origin_choice': {
        'header': 'Setting',
        'tooltip': '',
        'url': '',
        'default': ('', '')
    }
}


class SpaceGroup(LoggedPathDict):
    def __init__(self, crystal_system: Base, space_group_name_HM_ref: Base, space_group_IT_number: Base, origin_choice: Base):
        super().__init__(crystal_system=crystal_system, space_group_name_HM_ref=space_group_name_HM_ref,
                         space_group_IT_number=space_group_IT_number, origin_choice=origin_choice)
        self._log = logging.getLogger(__class__.__module__)

        self.setItemByPath(['crystal_system', 'header'], SG_DETAILS['crystal_system']['header'])
        self.setItemByPath(['crystal_system', 'tooltip'], SG_DETAILS['crystal_system']['tooltip'])
        self.setItemByPath(['crystal_system', 'url'], SG_DETAILS['crystal_system']['url'])

        self.setItemByPath(['space_group_name_HM_ref', 'header'], SG_DETAILS['space_group_name_HM_ref']['header'])
        self.setItemByPath(['space_group_name_HM_ref', 'tooltip'], SG_DETAILS['space_group_name_HM_ref']['tooltip'])
        self.setItemByPath(['space_group_name_HM_ref', 'url'], SG_DETAILS['space_group_name_HM_ref']['url'])

        self.setItemByPath(['space_group_IT_number', 'header'], SG_DETAILS['space_group_IT_number']['header'])
        self.setItemByPath(['space_group_IT_number', 'tooltip'], SG_DETAILS['space_group_IT_number']['tooltip'])
        self.setItemByPath(['space_group_IT_number', 'url'], SG_DETAILS['space_group_IT_number']['url'])

        self.setItemByPath(['origin_choice', 'header'], SG_DETAILS['origin_choice']['header'])
        self.setItemByPath(['origin_choice', 'tooltip'], SG_DETAILS['origin_choice']['tooltip'])
        self.setItemByPath(['origin_choice', 'url'], SG_DETAILS['origin_choice']['url'])
        self._log.debug('Spacegroup created: %s', self)

    def __repr__(self) -> str:
        return 'SpaceGroup: {} {} '.format(self['space_group_name_HM_ref'], self['origin_choice'])

    @classmethod
    def default(cls) -> 'SpaceGroup':
        crystal_system = Base(*SG_DETAILS['crystal_system']['default'])
        space_group_name_HM_ref = Base(*SG_DETAILS['space_group_name_HM_ref']['default'])
        space_group_IT_number = Base(*SG_DETAILS['space_group_IT_number']['default'])
        origin_choice = Base(*SG_DETAILS['origin_choice']['default'])
        return cls(crystal_system, space_group_name_HM_ref, space_group_IT_number, origin_choice)

    @classmethod
    def fromPars(cls, crystal_system: str, space_group_name_HM_ref: str, space_group_IT_number: int,
                 origin_choice: str) -> 'SpaceGroup':
        crystal_system = Base(crystal_system, SG_DETAILS['crystal_system']['default'][1])
        space_group_name_HM_ref = Base(space_group_name_HM_ref, SG_DETAILS['space_group_name_HM_ref']['default'][1])
        space_group_IT_number = Base(space_group_IT_number, SG_DETAILS['space_group_IT_number']['default'][1])
        origin_choice = Base(origin_choice, SG_DETAILS['origin_choice']['default'][1])

        return cls(crystal_system=crystal_system, space_group_name_HM_ref=space_group_name_HM_ref,
                   space_group_IT_number=space_group_IT_number, origin_choice=origin_choice)
