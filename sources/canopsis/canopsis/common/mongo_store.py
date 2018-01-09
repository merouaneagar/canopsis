#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
Manage mongodb connections.
"""

from __future__ import unicode_literals

from pymongo import MongoClient

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 27017
DEFAULT_DB_NAME = 'canopsis'


class MongoStore(object):
    """
    Distribute ready-to-use mongo collections.
    """

    CONF_PATH = 'etc/common/mongo_store.conf'
    CONF_CAT = 'DATABASE'

    def __init__(self, config):
        """
        To use a replicaset, just use a list of hosts in the configuration.

        Example:

        host = host1:27017,host2:27017

        :param config dict: a configuration object
        """
        self.config = config
        conf = self.config.get(self.CONF_CAT, {})
        self.db_name = conf.get('db', DEFAULT_DB_NAME)
        self.host = conf.get('host', DEFAULT_HOST)
        port = conf.get('port', DEFAULT_PORT)
        try:
            self.port = int(port)
        except ValueError:
            self.port = DEFAULT_PORT

        # missing from storage: journaling, sharding, retention ;;
        # cache_size, cache_autocommit, cache_ordered

        # missing from middleware: uri, protocol, data_type, data_scope, path,
        # auto_connect=true, safe=true, conn_timeout=20000, in_timeout=20000,
        # out_timeout=100, ssl=false, ssl_key, ssl_cert, user, pwd

        self._user = conf.get('user')
        self._pwd = conf.get('pwd')

        self._connect()

    def _connect(self):
        """
        Connect to the desired database.
        """
        self.client = MongoClient(host=self.host,
                                  port=self.port)[self.db_name]
        self.client.authenticate(self._user, self._pwd)

    def get_collection(self, name):
        """
        Return the desired collection.

        :param name: the name of the collection
        :rtype: Collection
        """
        return self.client[name]
