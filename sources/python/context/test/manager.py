#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2015 "Capensis" [http://www.capensis.com]
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

from unittest import TestCase, main
from canopsis.context.manager import Context


class BaseContextTest(TestCase):
    """Base class for context.
    """

    def setUp(self):
        self.context = Context(data_scope='test_context')
        self.context.remove()

    def tearDown(self):
        self.context.remove()


class ContextStorageTest(BaseContextTest):
    """Test access to the context storage.
    """

    def test_ctx_storage(self):
        """Test to access to the ctx storage.
        """
        context = self.context.context

        count_per_entity_type = 2

        # let's iterate on context items in order to create entities
        for n in range(1, len(context)):
            sub_context = context[:n]
            entity_context = {c: c for c in sub_context[1:]}
            entity = {}
            for i in range(count_per_entity_type):
                entity[Context.NAME] = str(i)
                self.context.put(
                    _type=context[n], context=entity_context, entity=entity
                )

        entities = self.context.find()

        self.assertEqual(
            len(entities),
            count_per_entity_type * (len(context) - 1) + len(context) - 2
        )

        for n in range(1, len(context)):
            sub_context = context[:n]
            entity_context = {c: c for c in sub_context[1:]}
            entities = self.context.find(
                _type=context[n], context=entity_context
            )

            self.assertEqual(
                len(entities),
                count_per_entity_type + (1 if n < (len(context) - 1) else 0)
            )

            _id = self.context.get_entity_id(entities[0])
            self.context.remove(ids=_id)
            entities = self.context.find(
                _type=context[n], context=entity_context
            )
            self.assertEqual(
                len(entities),
                count_per_entity_type - (0 if n < (len(context) - 1) else 1)
            )

            self.context.remove(_type=context[n], context=entity_context)
            entities = self.context.find(
                _type=context[n], context=entity_context
            )
            self.assertEqual(len(entities), 0)

    def test_incomplete_hierarchy(self):
        """Test to add elements where parents do not exists.
        """

        # first, ensure no entity exists
        # in constructing a context
        context = {}

        _context_keys = self.context.context[1:]
        # for all key in context.context keys
        for key in _context_keys:
            # check if entity does not exist
            entity = self.context.get(_type=key, names=key, context=context)
            context[key] = key  # update context with key
            self.assertIsNone(entity)

        # ensure entity does not exist
        entity = self.context.get(_type='test', names='test', context=context)
        self.assertIsNone(entity)

        # put entity in DB
        property_key = 'test'
        entity = {Context.NAME: 'test', property_key: 'test'}
        self.context.put(
            _type='test', entity=entity, context=context
        )

        # this time, check if parent have been putted
        context = {}
        # for all key in context.context keys
        for key in _context_keys:
            # check if entity does not exist
            entity = self.context.get(_type=key, names=key, context=context)
            context[key] = key  # update context with key
            self.assertIsNotNone(entity)
            self.assertNotIn(property_key, entity)

        # check if entity exists and if property key is in entity
        entity = self.context.get(_type='test', names='test', context=context)
        self.assertIsNotNone(entity)
        self.assertIn(property_key, entity)

        self.context.remove()

        del context['resource']
        # put entity in DB
        property_key = 'test'
        entity = {Context.NAME: 'test', property_key: 'test'}
        self.context.put(
            _type='test', entity=entity, context=context
        )
        # do the same with contex without resource

        # this time, check if parent have been putted
        context = {}
        # for all key in context.context keys
        for key in _context_keys[:-1]:
            # check if entity does not exist
            entity = self.context.get(_type=key, names=key, context=context)
            context[key] = key  # update context with key
            self.assertIsNotNone(entity)
            self.assertNotIn(property_key, entity)

        # check if entity exists and if property key is in entity
        entity = self.context.get(_type='test', names='test', context=context)
        self.assertIsNotNone(entity)
        self.assertIn(property_key, entity)

        # do the same in trying to put a resource
        self.context.remove()

        # put entity in DB
        property_key = 'test'
        entity = {Context.NAME: 'resource', property_key: 'test'}
        self.context.put(
            _type='resource', entity=entity, context=context
        )

        # this time, check if parent have been putted
        context = {}
        # for all key in context.context keys
        for key in _context_keys[:-1]:
            # check if entity does not exist
            entity = self.context.get(_type=key, names=key, context=context)
            self.assertIsNotNone(entity)
            self.assertNotIn(property_key, entity)
            context[key] = key  # update context with key

        # check if entity exists and if property key is in entity
        entity = self.context.get(
            _type='resource', names='resource', context=context
        )
        self.assertIsNotNone(entity)
        self.assertIn(property_key, entity)

        # do the same in trying to put a component
        self.context.remove()

        del context['component']
        # put entity in DB
        property_key = 'test'
        entity = {Context.NAME: 'component', property_key: 'test'}
        self.context.put(
            _type='component', entity=entity, context=context
        )

        # this time, check if parent have been putted
        context = {}
        # for all key in context.context keys
        for key in _context_keys[:-2]:
            # check if entity does not exist
            entity = self.context.get(_type=key, names=key, context=context)
            context[key] = key  # update context with key
            self.assertIsNotNone(entity)
            self.assertNotIn(property_key, entity)

        # check if entity exists and if property key is in entity
        entity = self.context.get(
            _type='component', names='component', context=context
        )
        self.assertIsNotNone(entity)
        self.assertIn(property_key, entity)


class ContextEntityTest(BaseContextTest):
    """Test for playing with entities.
    """

    def _assert_entity_id(self, entity, entity_id):

        _entity_id = self.context.get_entity_id(entity)
        self.assertEqual(_entity_id, entity_id)

    def test_get_entity_id_connector(self):
        """Test get_entity_id from a connector.
        """

        # assert to get a connector id
        entity = {
            'type': 'connector',
            'connector': 'c'
        }
        self._assert_entity_id(entity, '/connector/c')

    def test_get_entity_id_connector_name(self):
        """Test get_entity_id from a connector_name.
        """

        # assert to get a connector name id
        entity = {
            'type': 'connector_name',
            'connector': 'c',
            'connector_name': 'cn'
        }
        self._assert_entity_id(entity, '/connector_name/c/cn')

    def test_get_entity_id_component(self):
        """Test get_entity_id from a component.
        """

        entity = {
            'type': 'component',
            'connector': 'c',
            'connector_name': 'cn',
            'component': 'k'
        }
        self._assert_entity_id(entity, '/component/c/cn/k')

    def test_get_entity_id_resource(self):
        """Test get_entity_id from a resource.
        """

        entity = {
            'type': 'resource',
            'connector': 'c',
            'connector_name': 'cn',
            'component': 'k',
            'resource': 'r'
        }
        self._assert_entity_id(entity, '/resource/c/cn/k/r')

    def test_get_entity_id_other_component(self):
        """Test get_entity_id from a component other data.
        """

        entity = {
            'type': 'other',
            'connector': 'c',
            'connector_name': 'cn',
            'component': 'k',
            'other': 'o'
        }
        self._assert_entity_id(entity, '/other/c/cn/k/o')

    def test_get_entity_id_other_resource(self):
        """Test get_entity_id from a resource other data.
        """

        entity = {
            'type': 'other',
            'connector': 'c',
            'connector_name': 'cn',
            'component': 'k',
            'resource': 'r',
            'other': 'o'
        }
        self._assert_entity_id(entity, '/other/c/cn/k/r/o')


if __name__ == '__main__':
    main()
