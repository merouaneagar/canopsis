#!/usr/bin/env python
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

from unittest import TestCase, main

from cconfiguration import Configurable, Configuration, Category, Parameter

from os import remove

from tempfile import NamedTemporaryFile


class ConfigurableTest(TestCase):

    def setUp(self):

        self.conf_files = (
            NamedTemporaryFile().name,
            NamedTemporaryFile().name
        )

        self.configurable = Configurable()

        self.conf = Configuration(
            Category('A',
                Parameter('a', value='a'),
                Parameter('2', value=2, parser=int),
                Parameter('error', value='error', parser=float)),
            Category('B',
                Parameter('a', value='b'),
                Parameter('b', value='b')))

    def test_configuration_files(self):

        configurable = Configurable()
        configurable.conf_files = self.conf_files

        self.assertEqual(
            configurable.conf_files,
            self.conf_files)

        configurable = Configurable(
            conf_files=self.conf_files)

        self.assertEqual(
            configurable.conf_files,
            self.conf_files)

    def test_auto_conf(self):

        configurable = Configurable()

        self.assertTrue(configurable.auto_conf)

        configurable.auto_conf = False

        self.assertFalse(configurable.auto_conf)

    def test_logging_level(self):

        configurable = Configurable()

        self.assertTrue(configurable.log_lvl, 'INFO')

        configurable = Configurable(log_lvl='DEBUG')

        self.assertTrue(configurable.log_lvl, 'DEBUG')

        configurable.log_lvl = 'INFO'

        self.assertTrue(configurable.log_lvl, 'INFO')

    def test_configuration(self):

        # test to get from no file
        configurable = Configurable()

        conf = configurable.get_configuration()

        self.assertEqual(len(conf), len(self.conf))

        # test to get from files which do not exist
        configurable.conf_files = self.conf_files

        for conf_file in self.conf_files:
            try:
                remove(conf_file)
            except OSError:
                pass

        conf = configurable.get_configuration()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files
        for conf_file in self.conf_files:
            open(conf_file, 'w').close()

        conf = configurable.get_configuration()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files and empty parsing_rules
        conf = Configuration()
        configurable.get_configuration(conf=conf)

        self.assertEqual(len(conf), 0)

        # fill files
        configurable = Configurable(
            conf_files=self.conf_files)

        # add first category in conf file[0]
        configurable.set_configuration(
            conf_file=self.conf_files[0],
            conf=Configuration(self.conf['A']),
            manager=configurable._managers.split(',')[0])

        # add second category in conf file[1]
        configurable.set_configuration(
            conf_file=self.conf_files[1],
            conf=Configuration(self.conf['B']),
            manager=configurable._managers.split(',')[1])

        conf = configurable.get_configuration(
            fill=True, conf=self.conf)

        unified_configuration = conf.unify()
        parameters = unified_configuration[Configuration.VALUES]
        errors = unified_configuration[Configuration.ERRORS]

        self.assertTrue('a' in parameters and 'a' not in errors)
        self.assertEqual(parameters['a'].value, 'b')
        self.assertTrue('2' in parameters and '2' not in errors)
        self.assertEqual(parameters['2'].value, 2)
        self.assertTrue('b' in parameters and 'b' not in errors)
        self.assertEqual(parameters['b'].value, 'b')
        self.assertTrue('error' in errors and 'error' not in parameters)

    def test_reconfigure(self):

        self.assertTrue(self.configurable.auto_conf)

        conf = Configuration(
            Category('TEST',
                Parameter('auto_conf', value=False)))

        self.configurable.configure(conf=conf)

        self.assertFalse(self.configurable.auto_conf)

        self.assertTrue(self.configurable.log_lvl is 'INFO')

        conf = Configuration(
            Category('TEST',
                Parameter('log_lvl', value='DEBUG')))

        self.configurable.configure(conf=conf)

        self.assertTrue(self.configurable.log_lvl is 'INFO')

        self.configurable.once = True

        self.configurable.configure(conf=conf)

        self.assertTrue(self.configurable.log_lvl is 'DEBUG')

        self.assertFalse(self.configurable.once)

        self.configurable.log_lvl = 'INFO'

        self.configurable.auto_conf = True

        self.configurable.configure(conf=conf)

        self.assertTrue(self.configurable.log_lvl is 'DEBUG')

    def test_parser_inheritance(self):

        class _Configurable(Configurable):

            def _conf(self, *args, **kwargs):

                result = super(_Configurable, self)._conf(
                    *args, **kwargs)

                result += Category('PLOP')

                return result

        configurable = Configurable()

        _configurable = _Configurable()

        self.assertEqual(
            len(configurable.conf) + 1,
            len(_configurable.conf))

if __name__ == '__main__':
    main()