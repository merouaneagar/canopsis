#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import canopsis.common
import unittest
import configparser
from canopsis.common import root_path
from canopsis.common.amqp import AmqpPublisher, AmqpConnection
import xmlrunner


DEFAULT_AMQP_URL = 'amqp://guest:guest@localhost/'
DEFAULT_AMQP_EXCHANGE = 'test'
DEFAULT_CONF_FILE = "etc/amqp.conf"


class TestAmqp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = configparser.RawConfigParser()
        config.read(os.path.join(canopsis.common.root_path, DEFAULT_CONF_FILE))

        cls.amqp_url = "amqp://{0}:{1}@{2}:{3}/{4}".format(
            config["master"]["userid"],
            config["master"]["password"],
            config["master"]["host"],
            config["master"]["port"],
            config["master"]["virtual_host"])
        cls.amqp_exname = config["master"]["exchange_name"]

        cls.event = {
            'connector': 'test_amqp',
            'connector_name': 'test_amqp',
            'source_type': 'resource',
            'event_type': 'check',
            'component': 'test',
            'resource': 'test'
        }


class TestAmqpConn(TestAmqp):

    def test_connection_with_statement(self):
        with AmqpConnection(self.amqp_url) as amqp_conn:
            self.assertIsNotNone(amqp_conn.connection)
            self.assertIsNotNone(amqp_conn.channel)

    def test_connection_explicit(self):
        amqp_conn = AmqpConnection(self.amqp_url)
        amqp_conn.connect()

        self.assertIsNotNone(amqp_conn._connection)
        self.assertIsNotNone(amqp_conn._channel)

        amqp_conn.disconnect()

        self.assertIsNone(amqp_conn._connection)
        self.assertIsNone(amqp_conn._channel)


class TestAmqpPublisher(TestAmqp):

    def test_canopsis_event(self):
        with AmqpConnection(self.amqp_url) as ac:
            amqp_pub = AmqpPublisher(ac)
            amqp_pub.canopsis_event(self.event, self.amqp_exname)

    def test_bad_canopsis_event_raises(self):
        event = {}

        with AmqpConnection(self.amqp_url) as ac:
            amqp_pub = AmqpPublisher(ac)
            with self.assertRaises(KeyError):
                amqp_pub.canopsis_event(event, self.amqp_exname)

    def test_json_document(self):
        jdoc = {'bla': 'bla'}
        with AmqpConnection(self.amqp_url) as ac:
            amqp_pub = AmqpPublisher(ac)
            amqp_pub.json_document(jdoc, self.amqp_exname, '#')


if __name__ == '__main__':
    output = root_path + "/tmp/tests_report"
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output=output),
        verbosity=3)
