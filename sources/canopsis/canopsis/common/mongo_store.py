#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
Manage mongodb connections.
"""

from __future__ import unicode_literals

import time

from canopsis.confng import Configuration, Ini

from pymongo import MongoClient, MongoReplicaSetClient, ReadPreference
from pymongo.errors import AutoReconnect

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 27017
DEFAULT_DB_NAME = 'canopsis'

singletons_cache = {}

class MongoStore(object):
    """
    Distribute ready-to-use mongo collections.
    """

    CONF_PATH = 'etc/common/mongo_store.conf'
    CONF_CAT = 'DATABASE'

    @staticmethod
    def get_default(from_singleton=True):
        global singletons_cache

        cfg = Configuration.load(MongoStore.CONF_PATH, Ini)
        cfg_fingerprint = '.'.join(sorted(cfg.get(MongoStore.CONF_CAT, {}).values()))

        if cfg_fingerprint not in singletons_cache:
            print('NEW DB CONN')
            singletons_cache[cfg_fingerprint] = MongoStore(cfg)

        return singletons_cache.get(cfg_fingerprint)

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
        try:
            self.port = int(conf.get('port', DEFAULT_PORT))
        except ValueError:
            self.port = DEFAULT_PORT

        self.replicaset = conf.get('replicaset')
        self.read_preference = getattr(
            ReadPreference,
            conf.get('read_preference', 'SECONDARY_PREFERRED'),
            ReadPreference.SECONDARY_PREFERRED
        )

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
        if self.replicaset is None:
            self.conn = MongoClient(
                host=self.host,
                port=self.port,w=1,j=True
            )

        else:
            self.conn = MongoClient(
                'mongodb://{}:{}/?replicaSet={}'.format(self.host, self.port, self.replicaset),
                w=1,j=True, read_preference=self.read_preference
            )

        self.client = self.get_database(self.db_name)
        self.authenticate()

    def get_collection(self, name):
        """
        Return the desired collection.

        :param name: the name of the collection
        :rtype: Collection
        """
        return MongoStore.hr(getattr, self.client, name)

    def get_database(self, name):
        """
        Returns a raw pymongo Database object.
        """
        return MongoStore.hr(getattr, self.conn, name)

    def authenticate(self):
        """
        Authenticate against the requested database.
        """
        return MongoStore.hr(self.client.authenticate, self._user, self._pwd)

    def alive(self):
        return self.conn.alive() and self.conn is not None

    def close(self):
        return MongoStore.hr(self.conn.close)

    def fsync(self, **kwargs):
        return MongoStore.hr(self.conn.fsync, **kwargs)

    @staticmethod
    def hr(func, *args, **kwargs):
        """
        hr means "Handle Reconnect". This function will loop forever until
        the pymongo driver has succeeded to reconnect to the database.

        This works only when using a replicaset or sharding setup.

        Reconnections are tried every second.
        """
        while True:
            try:
                return func(*args, **kwargs)
            except AutoReconnect as exc:
                time.sleep(1)