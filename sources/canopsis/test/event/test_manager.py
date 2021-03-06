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
import unittest
from unittest import TestCase, main
from canopsis.common import root_path
from canopsis.common.middleware import Middleware
from canopsis.event.manager import Event as EventManager
import xmlrunner


class EventManagerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.event_storage = Middleware.get_middleware_by_uri('mongodb-default-testevent://')

    def setUp(self):
        self.event_manager = EventManager(event_storage=self.event_storage)
        self.fake_event = {
            'connector': 'fake_connector',
            'connector_name': 'fake_connector_name',
            'event_type': 'fake_event_type',
            'source_type': 'fake_source_type',
            'component': 'fake_component',

        }


class EventTest(EventManagerTest):

    def test_is_alert(self):
        alert = self.event_manager.is_alert(0)
        self.assertFalse(alert)

        for state in range(1, 4):
            alert = self.event_manager.is_alert(state)
            self.assertTrue(alert)

        # Test results border values
        for state in (-1, 4, 'test'):
            alert = self.event_manager.is_alert(state)
            self.assertIsNone(alert)

    def test_get_last_state(self):
        test_value = 'X'

        def mockfind(*args, **kwargs):
            return [{'state': test_value}]

        self.event_manager.find = mockfind
        state = self.event_manager.get_last_state(self.fake_event)
        self.assertEqual(state, test_value)

    def test_is_ack(self):
        event = {}

        is_ack = self.event_manager.is_ack(event)
        self.assertFalse(is_ack)

        event['ack'] = {}
        is_ack = self.event_manager.is_ack(event)
        self.assertFalse(is_ack)

        event['ack']['isAck'] = False
        is_ack = self.event_manager.is_ack(event)
        self.assertFalse(is_ack)

        event['ack']['isAck'] = True
        is_ack = self.event_manager.is_ack(event)
        self.assertTrue(is_ack)


if __name__ == '__main__':
    output = root_path + "/tmp/tests_report"
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output=output),
        verbosity=3)
