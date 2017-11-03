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

from a10_openstack_lib.resources import a10_device as a10_device_resources

import a10_neutron_lbaas.tests.db.test_base as test_base
import a10_neutron_lbaas.tests.unit.unit_config.helper as unit_config

from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import a10_device as a10_device
from a10_neutron_lbaas.neutron_ext.extensions import a10Device
from neutron.plugins.common import constants as nconstants


class TestA10DeviceDbMixin(test_base.UnitTestBase):

    def setUp(self):
        super(TestA10DeviceDbMixin, self).setUp()
        self._nm_patcher = mock.patch('neutron.manager.NeutronManager')
        nm = self._nm_patcher.start()
        nm.get_service_plugins.return_value = {
            nconstants.LOADBALANCERV2: mock.MagicMock()
        }

        self._config_cleanup = unit_config.use_config_dir()

        self.plugin = a10_device.A10DeviceDbMixin()

    def tearDown(self):
        self._config_cleanup()

        super(TestA10DeviceDbMixin, self).tearDown()

    def context(self):
        session = self.open_session()
        context = mock.Mock(session=session, tenant_id='fake-tenant-id')
        return context

    def envelope_vthunder(self, body):
        return {a10_device_resources.VTHUNDERS: body}

    def envelope_device(self, body):
        return {a10_device_resources.DEVICES: body}

    def envelope_device_key(self, body):
        return {a10_device_resources.DEVICE_KEYS: body}

    def envelope_device_value(self, body):
        return {a10_device_resources.DEVICE_VALUES: body}

class TestA10DeviceDb(TestA10DeviceDbMixin):

    def setUp(self):
        super(TestA10DeviceDb, self).setUp()

    def tearDown(self):
        super(TestA10DeviceDb, self).tearDown()

    def test_get_plugin_name(self):
        self.assertIsNot(self.plugin.get_plugin_name(), None)

    def test_get_plugin_description(self):
        self.assertIsNot(self.plugin.get_plugin_description(), None)

    def test_get_plugin_type(self):
        self.assertEqual(self.plugin.get_plugin_type(), constants.A10_DEVICE)

    def fake_device(self):
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

    def test_a10_device_create(self):
        instance = self.fake_device()
        context = self.context()
        result = self.plugin.create_a10_device(context, self.envelope_device(instance))
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

    def test_create_a10_device_options(self):
        instance = self.fake_device()
        instance.update(self.fake_device_options())
        context = self.context()
        result = self.plugin.create_a10_device(context, self.envelope(instance))
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

    def test_create_a10_device_default_port(self):
        instance = self.fake_device()
        instance['port'] = 80
        instance['protocol'] = 'http'
        context = self.context()
        result = self.plugin.create_a10_device(context, self.envelope_device(instance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        self.assertEqual(80, result['port'])

    def teat_update_a10_device(self):
        pass

    def test_delete_a10_device(self):
        pass

    def test_get_a10_device(self):
        instance = self.fake_device()
        create_context = self.context()
        create_result = self.plugin.create_a10_device(create_context,
                                                      self.envelope_develop(instance))
        create_context.session.commit()
        context = self.context()
        result = self.plugin.get_a10_device(context, create_result['id'])

        self.assertEqual(create_result, result)

    def test_get_a10_device_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Device.A10DeviceNotFoundError,
            self.plugin.get_a10_device,
            context,
            'fake-deviceinstance-id')

    def test_get_a10_devices(self):
        instance = self.fake_device()
        create_context = self.context()
        create_result = self.plugin.create_a10_device(create_context,
                                                      self.envelope_device(instance))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_devices(context)

        self.assertEqual([create_result], result)

    def fake_key(self):
        return {
            'name': 'fake-name',
            'description': 'fake-description',
            'project_id': 'fake-tenant-id',
        }

    def test_create_a10_device_key(self):
        instance = self.fake_device()
        context = self.context()
        result = self.plugin.create_a10_device(context, self.envelope_develop_key(instance))
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

    def test_create_a10_device_options(self):
        instance = self.fake_device()
        instance.update(self.fake_device_options())
        context = self.context()
        result = self.plugin.create_a10_device(context, self.envelope_develop_key(instance))
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

    def test_update_a10_device_key(self):
        pass

    def test_delete_a10_device_key(self):
        pass

    def test_get_a10_device_key(self):
        instance = self.fake_key()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_key(create_context,
                                                          self.envelope_develop_key(instance))
        create_context.session.commit()
        context = self.context()
        result = self.plugin.get_a10_device_key(context, create_result['id'])

        self.assertEqual(create_result, result)

    def test_get_a10_device_keys(self):
        instance = self.fake_key()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_key(create_context,
                                                          self.envelope_device_key(instance))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_device_keys(context)

        self.assertEqual([create_result], result)
