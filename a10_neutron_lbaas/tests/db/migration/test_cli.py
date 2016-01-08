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

import a10_neutron_lbaas.tests.db.session as session
import oslo_config
import oslo_config.fixture
import test_base

import a10_neutron_lbaas
import a10_neutron_lbaas.db.migration.cli as cli
import sqlalchemy
import sys

import a10_neutron_lbaas.db.models as models
import neutron.db.models_v2 as neutron_models
import neutron.db.servicetype_db as servicetype_db
import neutron_lbaas.db.loadbalancer.loadbalancer_db as lbaasv1_models
import neutron_lbaas.db.loadbalancer.models as lbaasv2_models


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

    def test_install_schema_matches_model_schema(self):
        self.run_cli('install')

        a10_models = session.a10_neutron_lbaas_models()

        inspection = sqlalchemy.inspect(self.connection)
        tables = inspection.get_table_names()

        missing_tables = [model.__tablename__ for model in a10_models if
                          model.__tablename__ not in tables]
        self.assertEqual([], missing_tables,
                         "The following tables weren't created by installing {0}".
                         format(missing_tables))

        for model in a10_models:
            columns = inspection.get_columns(model.__tablename__)

            actual_columns = sorted([
                {
                    'primary_key': True if c['primary_key'] else False,
                    'nullable': c['nullable'],
                    'default': c['default'],
                    'autoincrement': c['autoincrement'],
                    'type': c['type'].compile(dialect=self.connection.dialect),
                    'name': unicode(c['name'])
                }
                for c in columns],
                key=lambda x: x['name'])

            mapper = sqlalchemy.inspect(model)

            expected_columns = sorted([
                {
                    'primary_key': c.primary_key,
                    'nullable': c.nullable,
                    'default': c.server_default,
                    'autoincrement': c.autoincrement,
                    'type': c.type.compile(dialect=self.connection.dialect),
                    'name': unicode(c.name)
                }
                for c in mapper.columns
                if c.table.name == model.__tablename__],
                key=lambda x: x['name'])

            if (actual_columns != expected_columns):
                print ("The model and installed columns for {0} don't match".
                       format(model.__tablename__))
                print ("Model columns    ", [c['name'] for c in expected_columns])
                print ("Installed columns", [c['name'] for c in actual_columns])
            self.assertEqual(expected_columns, actual_columns)

    # Tests that upgrade order doesn't matter
    def test_upgrade_core_lbaasv1(self):
        self.run_cli('upgrade', 'core@head')
        self.run_cli('upgrade', 'lbaasv1@head')

    def test_upgrade_lbaasv1_core(self):
        self.run_cli('upgrade', 'lbaasv1@head')
        self.run_cli('upgrade', 'core@head')

    def test_upgrade_core_lbaasv2(self):
        self.run_cli('upgrade', 'core@head')
        self.run_cli('upgrade', 'lbaasv2@head')

    def test_upgrade_lbaasv2_core(self):
        self.run_cli('upgrade', 'lbaasv2@head')
        self.run_cli('upgrade', 'core@head')

    def test_upgrade_heads_downgrade_base(self):
        self.run_cli('upgrade', 'heads')
        self.run_cli('downgrade', 'base')

    def test_install_downgrade_base(self):
        self.run_cli('install')
        self.run_cli('downgrade', 'base')

    def add_lbaasv1_vip(self, provider):
        tenant_id = 'fake-tenant'
        status = 'FAKE'

        session = self.Session()
        network = models.default(neutron_models.Network)
        session.add(network)
        subnet = models.default(
            neutron_models.Subnet,
            network_id=network.id,
            ip_version=4,
            cidr='10.0.0.0/8')
        session.add(subnet)
        pool = models.default(
            lbaasv1_models.Pool,
            tenant_id=tenant_id,
            admin_state_up=False,
            status=status,
            subnet_id=subnet.id,
            protocol="TCP",
            lb_method="ROUND_ROBIN")
        vip = models.default(
            lbaasv1_models.Vip,
            tenant_id=tenant_id,
            admin_state_up=False,
            status=status,
            pool_id=pool.id,
            pool=[pool],
            protocol=pool.protocol,
            protocol_port=80)
        vip_id = vip.id
        session.add(vip)
        pra = models.default(
            servicetype_db.ProviderResourceAssociation,
            provider_name=provider,
            resource_id=pool.id)
        session.add(pra)
        session.commit()

        return vip_id

    def lbaasv1_drivers(self, device_key, provider):
        mock_config = mock.MagicMock(
            name='mock_config',
            devices={device_key: {'key': device_key}})
        mock_hooks = mock.MagicMock(
            name='mock_hooks',
            select_device=lambda x: mock_config.devices[device_key])
        mock_a10 = mock.MagicMock(
            name='mock_a10',
            spec=a10_neutron_lbaas.A10OpenstackLBV1,
            config=mock_config,
            hooks=mock_hooks)
        mock_driver = mock.MagicMock(
            name='mock_driver',
            a10=mock_a10)
        drivers = {'LOADBALANCER': ({provider: mock_driver}, provider)}

        return drivers

    def migrate_lbaasv1_vip(self):
        device_key = 'fake-device-key'
        provider = 'fake-provider'

        vip_id = self.add_lbaasv1_vip(provider)
        drivers = self.lbaasv1_drivers(device_key, provider)

        status = self.run_cli('install', drivers=drivers)

        return {
            'status': status,
            'vip_id': vip_id,
            'device_key': device_key
        }

    def test_migration_populate_lbaasv1(self):
        results = self.migrate_lbaasv1_vip()
        status = results['status']
        vip_id = results['vip_id']

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv1'].status)

        session = self.Session()
        slb = session.query(models.A10SLBV1).first()

        self.assertEqual(vip_id, slb.vip_id)

    def test_migration_populate_lbaasv1_tenant_appliance(self):
        results = self.migrate_lbaasv1_vip()
        status = results['status']
        device_key = results['device_key']

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv1'].status)

        session = self.Session()
        tenant_appliance = session.query(models.A10TenantAppliance).first()

        self.assertEqual(tenant_appliance.a10_appliance.device_key, device_key)

    def test_migration_remove_orphaned_a10_slb_v1(self):
        device_key = 'fake-device-key'
        provider = 'fake-provider'

        self.add_lbaasv1_vip(provider)
        drivers = self.lbaasv1_drivers(device_key, provider)

        self.run_cli('upgrade', '5a960cad849b', drivers=drivers)

        session1 = self.Session()
        session1.execute("DELETE FROM a10_slb_v1")
        session1.commit()

        status = self.run_cli('install', drivers=drivers)
        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv1'].status)

        session = self.Session()
        slbs = list(session.query(models.A10SLB))

        self.assertEqual([], slbs)

    def add_lbaasv2_lb(self, provider):
        tenant_id = 'fake-tenant'
        status = 'FAKE'

        session = self.Session()
        network = models.default(neutron_models.Network)
        session.add(network)
        subnet = models.default(
            neutron_models.Subnet,
            network_id=network.id,
            ip_version=4,
            cidr='10.0.0.0/8')
        session.add(subnet)
        lb = models.default(
            lbaasv2_models.LoadBalancer,
            tenant_id=tenant_id,
            admin_state_up=False,
            provisioning_status=status,
            operating_status=status,
            vip_subnet_id=subnet.id)
        lb_id = lb.id
        session.add(lb)
        pra = models.default(
            servicetype_db.ProviderResourceAssociation,
            provider_name=provider,
            resource_id=lb.id)
        session.add(pra)
        session.commit()

        return lb_id

    def lbaasv2_drivers(self, provider, device_key):
        mock_config = mock.MagicMock(
            name='mock_config',
            devices={device_key: {'key': device_key}})
        mock_hooks = mock.MagicMock(
            name='mock_hooks',
            select_device=lambda x: mock_config.devices[device_key])
        mock_a10 = mock.MagicMock(
            name='mock_a10',
            spec=a10_neutron_lbaas.A10OpenstackLBV2,
            config=mock_config,
            hooks=mock_hooks)
        mock_driver = mock.MagicMock(
            name='mock_driver',
            a10=mock_a10)
        drivers = {'LOADBALANCERV2': ({provider: mock_driver}, provider)}

        return drivers

    def migrate_lbaasv2_vip(self):
        device_key = 'fake-device-key'
        provider = 'fake-provider'

        lb_id = self.add_lbaasv2_lb(provider)
        drivers = self.lbaasv2_drivers(provider, device_key)

        status = self.run_cli('install', drivers=drivers)

        return {
            'status': status,
            'lb_id': lb_id,
            'device_key': device_key
        }

    def test_migration_populate_lbaasv2(self):
        results = self.migrate_lbaasv2_vip()
        status = results['status']
        lb_id = results['lb_id']

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv2'].status)

        session = self.Session()
        slb = session.query(models.A10SLBV2).first()

        self.assertEqual(lb_id, slb.lbaas_loadbalancer_id)

    def test_migration_populate_lbaasv2_tenant_appliance(self):
        results = self.migrate_lbaasv2_vip()
        status = results['status']
        device_key = results['device_key']

        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv2'].status)

        session = self.Session()
        tenant_appliance = session.query(models.A10TenantAppliance).first()

        self.assertEqual(tenant_appliance.a10_appliance.device_key, device_key)

    def test_migration_remove_orphaned_a10_slb_v2(self):
        device_key = 'fake-device-key'
        provider = 'fake-provider'

        self.add_lbaasv2_lb(provider)
        drivers = self.lbaasv2_drivers(provider, device_key)

        self.run_cli('upgrade', '2024607c4f06', drivers=drivers)

        session1 = self.Session()
        session1.execute("DELETE FROM a10_slb_v2")
        session1.commit()

        status = self.run_cli('install', drivers=drivers)
        self.assertEqual('UPGRADED', status['core'].status)
        self.assertEqual('UPGRADED', status['lbaasv2'].status)

        session = self.Session()
        slbs = list(session.query(models.A10SLB))

        self.assertEqual([], slbs)
