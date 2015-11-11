# Copyright 2015,  A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.from neutron.db import model_base

import mock
import os

import oslo_config
import oslo_config.fixture
import test_base

import a10_neutron_lbaas.db.migration.cli as cli
import sqlalchemy
import sys


class ARGV(object):

    def __init__(self, *argv):
        self.argv = argv

    def __enter__(self):
        self.original_argv = sys.argv
        sys.argv = self.argv
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.argv = self.original_argv


class TestCLI(test_base.UnitTestBase):

    def setUp(self):
        super(TestCLI, self).setUp()
        self.patch_create_engine = mock.patch.object(sqlalchemy,
                                                     'create_engine',
                                                     return_value=self.connection)
        self.patch_create_engine.__enter__()

    def tearDown(self):
        self.patch_create_engine.__exit__()
        super(TestCLI, self).tearDown()

    def run_cli(self, *argv, **kw):
        drivers = kw.get('drivers', mock.MagicMock())
        with oslo_config.fixture.Config(oslo_config.cfg.CONF):
            with ARGV(os.path.abspath(cli.__file__), *argv):
                return cli.run(drivers)

    def test_install(self):
        status = self.run_cli('install')

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv1'].status)
        self.assertEqual('UPGRADED', status['lbaasv2'].status)

    def test_install_lbaasv1(self):
        drivers = {'LOADBALANCER': mock.MagicMock()}
        status = self.run_cli('install', drivers=drivers)

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv1'].status)
        self.assertEqual('ERROR', status['lbaasv2'].status)

    def test_install_lbaasv2(self):
        drivers = {'LOADBALANCERV2': mock.MagicMock()}
        status = self.run_cli('install', drivers=drivers)

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('ERROR', status['lbaasv1'].status)
        self.assertEqual('UPGRADED', status['lbaasv2'].status)

    def test_upgrade_heads_downgrade_base(self):
        self.run_cli('upgrade', 'heads')
        self.run_cli('downgrade', 'base')

    def test_install_downgrade_base(self):
        self.run_cli('install')
        self.run_cli('downgrade', 'base')
