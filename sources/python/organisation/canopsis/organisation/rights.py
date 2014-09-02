# -*- coding: utf-8 -*-
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

from logging import DEBUG, ERROR, getLogger

from canopsis.configuration import conf_paths, add_category
from canopsis.middleware.manager import Manager

CATEGORY = 'RIGHTS'

@conf_paths('organisation/rights.conf')
@add_category(CATEGORY)
class Rights(Manager):

    DATA_SCOPE = 'rights'

    def __init__(
        self, data_scope=DATA_SCOPE,
        logging_level=ERROR,
        *args, **kwargs
    ):

        super(Rights, self).__init__(data_scope=data_scope, *args, **kwargs)


    # Generic getter
    def get_from_storage(self, s_type):
        def get_from_storage_(elem):
            return self[s_type + '_storage'].get_elements(
                ids=elem, query={'type':s_type}
                )
        return get_from_storage_


    def _configure(self, unified_conf, *args, **kwargs):

        super(Rights, self)._configure(
            unified_conf=unified_conf, *args, **kwargs)

        self.profile_storage = self['profile_storage']
        self.composite_storage = self['composite_storage']
        self.role_storage = self['role_storage']
        self.action_storage = self['action_storage']
        self.user_storage = self['user_storage']

        self.get_profile = self.get_from_storage('profile')
        self.get_action = self.get_from_storage('action')
        self.get_composite = self.get_from_storage('composite')
        self.get_role = self.get_from_storage('role')
        self.get_user = self.get_from_storage('user')


    # Add an action to the referenced action
    def add(self, a_id, a_desc):
        """
        Args:
            a_id: id of the action to reference
            a_desc: description of the action to reference
        Returns:
            A document describing the effect of the put_elements
            if the action was created
            ``None`` otherwise
        """

        action = {'type': 'action',
                  'desc': a_desc}
        return self['action_storage'].put_element(a_id, action)


    # Check if an entity has the flags for a specific rigjt
    # The entity must have a rights field with a rights maps within
    def check(self, entity, right_id, checksum):
        """
        Args:
            entity: entity to be checked
            right_id: right to be checked
            checksum: minimum flags needed
        Returns:
            ``True`` if the entity has enough permissions on the right
            ``False`` otherwise
        """

        if not entity or not entity.get('rights', None):
            return False

        found = entity['rights'].get(right_id, None)
        if (found and found.get('checksum', 0) & checksum >= checksum):
            return True

        return False


    # Check if an user has the flags for a specific right
    # Each of the user's entities (Role, Profile, and Composites)
    # will be checked For now, you must specify the user's role
    def check_rights(self, role, right_id, checksum):
        """
        Args:
            role: user's role to be checked
            right_id: right to be checked
            checksum: minimum flags needed
        Returns:
            ``True`` if the user's role has enough permissions
            ``False`` otherwise
        """

        role = self.get_role(role)
        profiles = self.get_profile(role['profile'])

        # Do not edit the following for a double for loop
        # list comprehensions are much faster
        composites = [self['composite_storage'][x]
                      for y in profiles
                      for x in y['composite']]

        # check in the role's comsposite
        if ((role and self.check(role, right_id, checksum)) or
            # check in the profile's composite
            (len(profiles) and any(self.check(x, right_id, checksum)
                                   for x in profiles)) or
            # check in the profile's groups composites
            (len(composites) and any(self.check(x, right_id, checksum)
                                     for x in composites))):
            return True

        return False

    # Add a right to the entity linked
    # If the right already exists, the checksum will be summed accordingly
    # checksum |= old_checksum
    # entity can be a role, a profile, or a composite
    def add_right(self, e_name, e_type, right_id, checksum,
            **kwargs):
        """
        Args:
            e_name: name of the entity to add the right to
            e_type: type of the entity
            right_id: right to be modified
            checksum: flags to add
        Returns:
            The checksum of the right if the flags were added
            ``0`` otherwise
        """

        # Action not referenced, can't create a right
        if not self.get_action(right_id):
            print (
                'Can not add right {0} to entity {1}: action is not referenced'.format(right_id, e_name))
            return 0

        entity = None

        e_type += '_storage'

        if e_type in self:
            entity = self[e_type].get_elements(ids=e_name)

        if not entity:
            return 0

        if not entity.get('rights', None):
            entity['rights'] = {}

        # If it does not exist, create it
        if not self.check(entity, right_id, 0):
            entity['rights'].update({right_id: {'type': 'right',
                                                'checksum': checksum
                                                }
                                     })
        else:
            entity['rights'][right_id]['checksum'] |= checksum

        # Add the new context and other fields, if any
        for key in kwargs:
            if kwargs[key]:
                entity['rights'][right_id][key] = context

        self[e_type].put_element(e_name, entity)
        return entity['rights'][right_id]['checksum']


    # Delete the checksum right of the entity linked
    # new_checksum ^= checksum
    def remove_right(self, entity, e_type, right_id, checksum):
        """
        Args:
            entity: entity to delete the right from
            e_type: type of the entity
            right_id: right to be modified
            checksum: flags to remove
         Returns:
            The checksum of the right if it was modified
            ``0`` otherwise
         """

        entity = self[e_type + '_storage'].get_elements(ids=entity)

        if (entity['rights']
            and entity['rights'][right_id]
            and entity['rights'][right_id]['checksum'] >= checksum):

            # remove the permissions passed in checksum
            entity['rights'][right_id]['checksum'] ^= checksum

            # If all the permissions were removed from the right, delete it
            if not entity['rights'][right_id]['checksum']:
                del entity['rights'][right_id]
                self[e_type + "_storage"].put_element(entity['_id'], entity)
                return 0

            self[e_type + "_storage"].put_element(entity['_id'], entity)
            return entity['rights'][right_id]['checksum']

        return 0


    # Create a new rights composite composed of the rights passed in comp_rights
    # comp_rights should be a map of rights referenced in the action catalog
    def create_composite(self, comp_name, comp_rights):
        """
        Args:
            comp_name: id of the composite to create
            comp_rights: map of rights to init the composite with
        Returns:
            The name of the composite if it was created
            ``None`` otherwise
        """

        # Do nothing if it already exists
        if self.get_composite(comp_name):
            return None

        new_comp = {'type': 'composite',
                    'rights': {}
                    }

        self.composite_storage.put_element(comp_name, new_comp)

        # Use add_right to check if the action is referenced
        for right_id in comp_rights:
            self.add_right(comp_name,
                           'composite',
                           right_id,
                           comp_rights[right_id]['checksum'])

        return comp_name


    # Create a new profile composed of the composites p_composites
    #   and which name will be p_name
    # If the profile already exists, composites from p_composites
    #   that are not already in the profile's composites will be added
    def create_profile(self, p_name, p_composites):
        """
        Args:
            p_name: id of the profile to be created
            p_compsites: list of composites to init the Profile with
        Returns:
            The name of the profile if it was created
            ``None`` otherwise
        """

        # Do nothing if it already exists
        if self.get_profile(p_name):
            return None

        new_profile = {'type':'profile',
                       'composites': []
                       }

        self.profile_storage.put_element(p_name, new_profile)

        for comp in p_composites:
            self.add_composite(p_name, 'profile', comp)

        return p_name


    # Delete entity of id e_name
    # t_type is the storage to check for relations
    # entity can be a profile, or composite
    def delete_entity(self, e_name, e_type):
        """
        Args:
            e_name: id of the entity to be deleted
            e_type: type of the entity
        Returns:
            ``True`` if the entity was deleted
            ``False`` otherwise
        """

        from_storage = e_type + '_storage'
        t_types = {'profile': 'role',
                   'composite': 'profile',
                   'role': 'user'}
        t_type = t_types[e_type]
        to_storage = t_type + '_storage'

        if self[from_storage].get_elements(ids=e_name):
            self[from_storage].remove_elements(e_name)

            # remove the entity from every other entities that use it
            for entity in self[to_storage].get_elements(query={'type':t_type}):
                if e_type in entity and e_name in entity[e_type]:
                    entity[e_type].remove(e_name)
                    self[to_storage].put_element(entity['_id'], entity)

            return True

        return False


    # to be removed when user module is created
    def delete_role(self, r_name):
        """
        Args:
            r_name: id of the role to be deleted
        Returns:
            ``True`` if the role was deleted
            ``False`` otherwise
        """

        return self.delete_entity(r_name, 'role')



    # delete_entity wrapper
    def delete_profile(self, p_name):
        """
        Args:
            p_name: id of the profile to be deleted
        Returns:
            ``True`` if the profile was deleted
            ``False`` otherwise
        """

        return self.delete_entity(p_name, 'profile')


    # delete_entity wrapper
    def delete_composite(self, c_name):
        """
        Args:
            c_name: id of the composite to be deleted
        Returns:
            ``True`` if the composite was deleted
            ``False`` otherwise
        """

        return self.delete_entity(c_name, 'composite')


    # Add the composite named comp_name to the entity
    # If the composite does not exist and
    #   comp_rights is specified it will be created first
    # entity can be a profile or a role
    def add_composite(self, e_name, e_type, comp_name, comp_rights=None):
        """
        Args:
            e_name: name of the entity to be modified
            e_type: type of the entity
            comp_name: id of the composite to add to the entity
            comp_rights: specified if the composite has to be created beforehand
        Returns:
            ``True`` if the composite was added to the entity
            ``False`` otherwise
        """

        e_type += '_storage'

        if not self.get_composite(comp_name):
            if comp_rights:
                self.create_composite(comp_rights, comp_name)
            else:
                return False

        entity = self[e_type].get_elements(ids=e_name)
        if not 'composite' in entity or not comp_name in entity['composite']:
            entity.setdefault('composite', []).append(comp_name)
            self[e_type].put_element(e_name, entity)

        return True


    # add_composite wrapper
    def add_comp_profile(self, e_name, comp_name, comp_rights=None):
        self.add_composite(e_name, 'profile', comp_name, comp_rights)


    # add_composite wrapper
    def add_comp_role(self, e_name, comp_name, comp_rights=None):
        self.add_composite(e_name, 'role', comp_name, comp_rights)


    # add_composite wrapper
    def add_comp_user(self, e_name, comp_name, comp_rights=None):
        self.add_composite(e_name, 'user', comp_name, comp_rights)


    # Add the profile of name p_name to the role
    # If the profile does not exists and p_composites is specified
    #    it will be created first
    def add_profile(self, role, p_name, p_composites=None):
        """
        Args:
            role: id of the role to add the Profile to
            p_name: name of the Profile to be added
            p_composites: specified if the profile has to be created beforehand
        Returns:
            ``True`` if the profile was created
            ``False`` otherwise
        """

        profile = self.get_profile(p_name)
        if not profile:
            if p_composites:
                self.create_profile(p_name, p_composites)
            else:
                return False

        # retrieve the profile
        if profile:
            s_role = self.get_role(role)

            if not 'profile' in s_role or not p_name in s_role['profile']:
                s_role.setdefault('profile', []).append(p_name)
                self.role_storage.put_element(role, s_role)

            return True


    # Add the profile of name p_name to the role
    # If the profile does not exists and p_composites is specified
    #    it will be created first
    def add_role(self, u_name, r_name, r_profile=None):
        """
        Args:
            u_name: id of the user to add the role to
            r_name: name of the role to be added
            r_composites: specified if the role has to be created beforehand
        Returns:
            ``True`` if the profile was created
            ``False`` otherwise
        """

        role = self.get_role(r_name)
        if not role:
            if r_profile:
                self.create_role(r_name, r_profile)
            else:
                return False

        # retrieve the profile
        if role:
            s_user = self.get_user(u_name)

            if not 'role' in s_user or not r_name in s_user['role']:
                s_user.setdefault('role', []).append(r_name)
                self.user_storage.put_element(u_name, s_user)

            return True


    # Remove the entity e_name from from_name
    # from_name can be a profile or a role
    # e_name can be a profile or a composite
    def remove_entity(self, from_name, from_type, e_name, e_type):
        entity = self[from_type + '_storage'].get_elements(
            query={'type': from_type}, ids=from_name)

        if e_type in entity and e_name in entity[e_type]:
            entity[e_type].remove(e_name)
            self[from_type + '_storage'].put_element(from_name, entity)
            return True

        return False

    # remove_entity wrapper
    def remove_composite(self, e_name, e_type, comp_name):
        """
        Args:
            e_name: name of the entity to be modified
            e_type: type of the entity
            comp_name: id of the composite to remove from the entity
        Returns:
            ``True`` if the composite was removed from the entity
            ``False`` otherwise
        """

        return self.remove_entity(e_name, e_type, comp_name, 'composite')


    # remove_composite wrapper
    def remove_comp_role(self, r_name, c_name):
        """
        Args:
            r_name: role to removed the composite from
            c_name: composite to remove
        Return:
            ``True`` if the composite was removed from the role
            ``False`` otherwise
        """

        return self.remove_composite(r_name, 'role', c_name)


    # remove_composite wrapper
    def remove_comp_profile(self, p_name, c_name):
        """
        Args:
            p_name: profile to removed the composite from
            c_name: composite to remove
        Return:
            ``True`` if the composite was removed from the profile
            ``False`` otherwise
        """

        return self.remove_composite(p_name, 'profile', c_name)

    # remove_composite wrapper
    def remove_comp_user(self, u_name, c_name):
        """
        Args:
            u_name: user to removed the composite from
            c_name: composite to remove
        Return:
            ``True`` if the composite was removed from the profile
            ``False`` otherwise
        """

        return self.remove_composite(u_name, 'user', c_name)


    # remove_entity wrapper
    def remove_profile(self, r_name, p_name):
        """
        Args:
            r_name: id of the role to remove the Profile from
            p_name: name of the Profile to be removed
        Returns:
            ``True`` if the profile was removed from the entity
            ``False`` otehrwise
        """

        return self.remove_entity(r_name, 'role', p_name, 'profile')


    # remove_entity wrapper
    def remove_role(self, u_name, r_name):
        """
        Args:
            u_name: id of the user to remove the role from
            r_name: name of the role to be removed
        Returns:
            ``True`` if the role was removed from the entity
            ``False`` otehrwise
        """

        return self.remove_entity(u_name, 'user', r_name, 'role')


    # Create a new role composed of the profile r_profile
    #   and which name will be r_name
    # Any extra field can be specified in the kwargs
    # If the role already exists, the profile will be changed for r_profile
    def create_role(self, r_name, r_profile):
        """
        Args:
            r_name: id of the Role to be created
            r_profile: id of the Profile to init the Role with
        Returns:
            ``Name`` of the role if it was created
        """

        if self.get_role(r_name):
            return r_name

        new_role = {'type': 'role'}
        if isinstance(r_profile, list):
            new_role['profile'] = r_profile
        else:
            new_role.setdefault('profile', []).append(r_profile)
        self.role_storage.put_element(r_name, new_role)
        return r_name


    def create_user(self, u_id, u_role, contact=None):
        """
        Args:
            u_nick: nick of the user to create, usually first
                    letter of first name and last name (i.e.:
                    jdoe for John Doe)
            u_role: role to init the user with
            contact: map containing full name, email, adress,
                     and/or phone number of the user
        Returns:
            Map of the newly created user
        """

        user = self.get_user(u_id)

        if user:
            return user

        if not self.get_role(u_role):
            return None

        user = {'type': 'user',
                'role': u_role}

        if contact:
            user['contact'] = contact

        self.user_storage.put_element(u_id, user)
        return user


    def set_user_fields(self, u_id, fields):
        """
        Args:
            u_id: id of the user which fields to change
            fields: map of fields to change and their new values
        Returns:
            Map of the modified user
        """

        user = self.get_user(u_id)

        supported_fields={'name', 'email', 'address', 'phone'}

        for key in fields:
            if key in supported_fields:
                user.setdefault('contact', {})[key] = fields[key]

        self.user_storage.put_element(u_id, user)
        return user


    def set_user_name(self, u_id, u_name):
        """
        Args:
            u_id: id of the user which name to change
            u_name: new name
        Returns:
            Map of the modified user
        """
        return self.set_user_field(u_id, {'name': u_name})

    def set_user_email(self, u_id, u_email):
        """
        Args:
            u_id: id of the user which email to change
            u_email: new email
        Returns:
            Map of the modified user
        """
        return self.set_user_field(u_id, {'email': u_email})


    def set_user_address(self, u_id, u_address):
        """
        Args:
            u_id: id of the user which address to change
            u_address: new address
        Returns:
            Map of the modified user
        """
        return self.set_user_field(u_id, {'address': u_address})


    def set_user_phone(self, u_id, u_phone):
        """
        Args:
            u_id: id of the user which phone to change
            u_phone: new phone
        Returns:
            Map of the modified user
        """
        return self.set_user_field(u_id, {'phone': u_phone})

