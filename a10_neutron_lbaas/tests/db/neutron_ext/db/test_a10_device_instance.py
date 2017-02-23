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
#    under the License.

import mock

from a10_openstack_lib.resources import a10_device_instance as a10_device_instance_resources

import a10_neutron_lbaas.tests.db.test_base as test_base
import a10_neutron_lbaas.tests.unit.unit_config.helper as unit_config

from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import a10_device_instance as a10_device_instance
from a10_neutron_lbaas.neutron_ext.extensions import a10DeviceInstance
from neutron.plugins.common import constants as nconstants


class TestA10DeviceInstanceDbMixin(test_base.UnitTestBase):

    def setUp(self):
        super(TestA10DeviceInstanceDbMixin, self).setUp()
        self._nm_patcher = mock.patch('neutron.manager.NeutronManager')
        nm = self._nm_patcher.start()
        nm.get_service_plugins.return_value = {
            nconstants.LOADBALANCERV2: mock.MagicMock()
        }

        self._config_cleanup = unit_config.use_config_dir()

        self.plugin = a10_device_instance.A10DeviceInstanceDbMixin()

    def tearDown(self):
        self._config_cleanup()

        super(TestA10DeviceInstanceDbMixin, self).tearDown()

    def context(self):
        session = self.open_session()
        context = mock.Mock(session=session, tenant_id='fake-tenant-id')
        return context

    def envelope(self, body):
        return {a10_device_instance_resources.RESOURCE: body}


class TestA10DeviceInstanceDb(TestA10DeviceInstanceDbMixin):

    def setUp(self):
        super(TestA10DeviceInstanceDb, self).setUp()

    def tearDown(self):
        super(TestA10DeviceInstanceDb, self).tearDown()

    def fake_deviceinstance(self):
        return {
            'name': 'fake-name',
            'description': 'fake-description',
            'host': 'fake-host',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password',
            'autosnat': False,
            'default_virtual_server_vrid': None,
            'ipinip': False,
            'use_float': False,
            'v_method': 'LSI',
            'shared_partition': 'shared',
            'write_memory': False,
            'nova_instance_id': 'fake-instance-id',
            'project_id': 'fake-tenant-id',
            'protocol': 'https',
            'port': 442
        }

    def fake_deviceinstance_options(self):
        return {
            'protocol': 'http',
            'port': 12345
        }

    def test_a10_device_instance(self):
        instance = self.fake_deviceinstance()
        context = self.context()
        result = self.plugin.create_a10_device_instance(context, self.envelope(instance))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(instance)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id

            })
        self.assertEqual(expected, result)

    def test_create_a10_device_instance_options(self):
        instance = self.fake_deviceinstance()
        instance.update(self.fake_deviceinstance_options())
        context = self.context()
        result = self.plugin.create_a10_device_instance(context, self.envelope(instance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        expected = instance.copy()
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id
            })

        self.assertEqual(expected, result)

    def test_create_a10_device_instance_default_port(self):
        instance = self.fake_deviceinstance()
        instance['port'] = 80
        instance['protocol'] = 'http'
        context = self.context()
        result = self.plugin.create_a10_device_instance(context, self.envelope(instance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        self.assertEqual(80, result['port'])

    def test_get_a10_device_instance(self):
        instance = self.fake_deviceinstance()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_instance(create_context,
                                                               self.envelope(instance))
        create_context.session.commit()
        context = self.context()
        result = self.plugin.get_a10_device_instance(context, create_result['id'])

        self.assertEqual(create_result, result)

    def test_get_a10_device_instance_not_found(self):
        context = self.context()
        self.assertRaises(
            a10DeviceInstance.A10DeviceInstanceNotFoundError,
            self.plugin.get_a10_device_instance,
            context,
            'fake-deviceinstance-id')

    def test_get_a10_device_instances(self):
        instance = self.fake_deviceinstance()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_instance(create_context,
                                                               self.envelope(instance))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_device_instances(context)

        self.assertEqual([create_result], result)

    def test_get_plugin_name(self):
        self.assertIsNot(self.plugin.get_plugin_name(), None)

    def test_get_plugin_description(self):
        self.assertIsNot(self.plugin.get_plugin_description(), None)

    def test_get_plugin_type(self):
        self.assertEqual(self.plugin.get_plugin_type(), constants.A10_DEVICE_INSTANCE)
