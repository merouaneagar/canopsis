#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2018 "Capensis" [http://www.capensis.com]
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

"""
Adapter for view object.
"""

from __future__ import unicode_literals

from uuid import uuid4

from canopsis.common.collection import MongoCollection
from canopsis.common.mongo_store import MongoStore
from canopsis.views.enums import ViewField, GroupField, ViewResponseField

VIEWS_COLLECTION = 'views'
GROUPS_COLLECTION = 'viewgroups'


class NonEmptyGroupError(Exception):
    """
    A NonEmptyGroupError is an Exception that is raised when trying to remove a
    non-empty group.
    """


class InvalidViewError(Exception):
    """
    An InvalidViewError is an exception that is raised when a view is invalid.
    """
    def __init__(self, message):
        super(InvalidViewError, self).__init__(message)
        self.message = message


class InvalidGroupError(Exception):
    """
    An InvalidGroupError is an exception that is raised when a view is invalid.
    """
    def __init__(self, message):
        super(InvalidGroupError, self).__init__(message)
        self.message = message


class InvalidFilterError(Exception):
    """
    An InvalidFilterError is an exception that is raised when a filter is
    invalid.
    """
    def __init__(self, message):
        super(InvalidFilterError, self).__init__(message)
        self.message = message


class ViewAdapter(object):
    """
    Adapter for the view collection.
    """
    def __init__(self, logger):
        self.logger = logger
        self.view_collection = MongoCollection(
            MongoStore.get_default().get_collection(VIEWS_COLLECTION))
        self.group_collection = MongoCollection(
            MongoStore.get_default().get_collection(GROUPS_COLLECTION))

    def get_by_id(self, view_id):
        """
        Get a view given its id.

        :param str view_id: the id of the view.
        """
        return self.view_collection.find_one({
            ViewField.id: view_id
        })

    def create(self, view):
        """
        Create a new view and return its id.

        :param Dict[str, Any] view:
        :rtype: str
        """
        view_id = str(uuid4())

        view[ViewField.id] = view_id
        self.validate(view_id, view)

        self.view_collection.insert(view)
        return view_id

    def update(self, view_id, view):
        """
        Update a view given its id.

        :param str view_id: the id of the view.
        :param Dict[str, Any] view:
        """
        self.validate(view_id, view)

        self.view_collection.update({
            ViewField.id: view_id
        }, view, upsert=False)

    def remove_with_id(self, view_id):
        """
        Remove a view given its id.

        :param str view_id: the id of the view.
        """
        self.view_collection.remove({
            ViewField.id: view_id
        })

    def list(self, name=None, title=None):
        """
        Return a list of views, optionally filtered by name or title.

        :param str name:
        :param str title:
        :rtype: List[Dict[str, Any]]
        :raises: InvalidFilterError
        """
        view_filter = {}

        if name is not None and title is not None:
            raise InvalidFilterError(
                'Cannot filter both by name and by title.')

        if name is not None:
            view_filter[ViewField.name] = name
        if title is not None:
            view_filter[ViewField.title] = title

        views = self.view_collection.find(view_filter)
        groups = self.group_collection.find({})

        response_groups = {}

        for group in groups:
            group_id = group[GroupField.id]

            del group[GroupField.id]
            group[GroupField.views] = []

            response_groups[group_id] = group

        for view in views:
            try:
                group_id = view[ViewField.group_id]
            except KeyError:
                # This should never happen as long as the collections are only
                # modified using the API
                self.logger.exception(
                    'The view {0} is missing the group_id field.'.format(
                        view[ViewField.id]))
                continue

            try:
                response_groups[group_id][GroupField.views].append(view)
            except KeyError:
                # This should never happen as long as the collections are only
                # modified using the API
                self.logger.exception('No group with id: {0}'.format(group_id))

        return {
            ViewResponseField.groups: response_groups
        }

    def validate(self, view_id, view):
        """
        Check that the view is valid, return InvalidViewError if it is not.

        :param Dict[str, Any] view:
        """
        # Validate id field
        if view.get(ViewField.id, view_id) != view_id:
            raise InvalidViewError(
                'The {0} field should not be modified'.format(ViewField.id))

        # Validate group_id field
        if ViewField.group_id not in view:
            raise InvalidViewError('The view should have a group_id field.')

        group_id = view[ViewField.group_id]
        group = self.group_collection.find_one({
            GroupField.id: group_id
        })
        if not group:
            raise InvalidViewError('No group with id: {0}'.format(group_id))

        # Validate name field
        if ViewField.name not in view:
            raise InvalidViewError('The view should have a name field.')

        view_name = view[ViewField.name]
        same_name_view = self.view_collection.find_one({
            ViewField.id: {'$ne': view_id},
            ViewField.name: view_name
        })
        if same_name_view:
            raise InvalidViewError(
                'There is already a view with the name: {0}'.format(
                    view_name))

        # Validate title field
        if ViewField.title not in view:
            raise InvalidViewError('The view should have a title field.')


class GroupAdapter(object):
    """
    Adapter for the group collection.
    """
    def __init__(self, logger):
        self.logger = logger
        self.group_collection = MongoCollection(
            MongoStore.get_default().get_collection(GROUPS_COLLECTION))
        self.view_collection = MongoCollection(
            MongoStore.get_default().get_collection(VIEWS_COLLECTION))

    def get_by_id(self, group_id, name=None, title=None):
        """
        Get a group given its id.

        :param str group_id: the id of the group.
        :param str name:
        :param str title:
        :rtype: Dict[str, Any]
        """
        group = self.group_collection.find_one({
            GroupField.id: group_id
        })

        if group:
            group[GroupField.views] = self.get_views(group_id, name, title)

        return group

    def get_views(self, group_id, name=None, title=None):
        """
        Returns the list of views of a group, optionally filtered by name or
        title.

        :param str group_id:
        :param str name:
        :param str title:
        :rtype: List[Dict[str, Any]]
        :raises: InvalidFilterError
        """
        view_filter = {
            ViewField.group_id: group_id
        }

        if name is not None and title is not None:
            raise InvalidFilterError(
                'Cannot filter both by name and by title.')

        if name is not None:
            view_filter[ViewField.name] = name
        if title is not None:
            view_filter[ViewField.title] = title

        return list(self.view_collection.find(view_filter))

    def is_empty(self, group_id):
        """
        Return True if a group is empty.

        :param str group_id:
        :rtype: bool
        """
        return self.view_collection.find({
            ViewField.group_id: group_id
        }).limit(1).count() == 0

    def create(self, group):
        """
        Create a new group.

        :param Dict group:
        :rtype: str
        :raises: InvalidGroupError
        """
        group_id = str(uuid4())

        group[GroupField.id] = group_id
        self.validate(group_id, group)

        self.group_collection.insert(group)
        return group_id

    def update(self, group_id, group):
        """
        Update a group given its id.

        :param str group_id:
        :param Dict group:
        :raises: InvalidGroupError
        """
        self.validate(group_id, group)

        self.group_collection.update({
            GroupField.id: group_id
        }, group, upsert=False)

    def remove_with_id(self, group_id):
        """
        Remove a group given its id.

        :param str group_id:
        :raises: NonEmptyGroupError
        """
        if not self.is_empty(group_id):
            raise NonEmptyGroupError()

        self.group_collection.remove({
            GroupField.id: group_id
        })

    def list(self, name=None):
        """
        Return a list of groups, optionally filtered by name.

        :param str name:
        :rtype: List[Dict[str, Any]]
        """
        group_filter = {}

        if name is not None:
            group_filter[GroupField.name] = name

        return list(self.group_collection.find(group_filter))

    def validate(self, group_id, group):
        """
        Check that the gorup is valid, return InvalidGroupError if it is not.

        :param Dict[str, Any] view:
        :raises: InvalidGroupError
        """
        if group.get(GroupField.id, group_id) != group_id:
            raise InvalidGroupError(
                'The {0} field should not be modified'.format(GroupField.id))

        if GroupField.name not in group:
            raise InvalidGroupError('The group should have a name field.')

        group_name = group[GroupField.name]
        same_name_group = self.group_collection.find_one({
            GroupField.id: {'$ne': group_id},
            GroupField.name: group_name
        })
        if same_name_group:
            raise InvalidGroupError(
                'There is already a group with the name: {0}'.format(
                    group_name))

    def exists(self, group_id):
        """
        Return True if a group exists.

        :param str group_id:
        :rtype: bool
        """
        group = self.group_collection.find_one({
            GroupField.id: group_id
        })
        return group is not None
