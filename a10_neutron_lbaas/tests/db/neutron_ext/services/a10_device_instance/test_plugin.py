# Copyright 2015-2016, A10 Networks
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
import uuid

import a10_openstack_lib.resources.a10_device_instance as resources

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.neutron_ext.common.constants as constants
from a10_neutron_lbaas.neutron_ext.extensions import a10DeviceInstance
import a10_neutron_lbaas.neutron_ext.services.a10_device_instance.plugin as plugin
from a10_neutron_lbaas.tests.db.neutron_ext.db import test_a10_device_instance


class TestPlugin(test_a10_device_instance.TestA10DeviceInstanceDbMixin):

    def setUp(self):
        super(TestPlugin, self).setUp()
        self.plugin = plugin.A10DeviceInstancePlugin()
        self.target = self.plugin

        self.maxDiff = None

        self.instance_manager = mock.MagicMock()
        self.instance_manager.create_device_instance.side_effect = self.fake_instance

        self.vthunder_defaults = a10_config.A10Config().get_vthunder_config()

        self._im_patcher = mock.patch(
            'a10_neutron_lbaas.vthunder.instance_manager.InstanceManager.from_config',
            return_value=self.instance_manager)
        self._im_patcher.start()

    def tearDown(self):
        self._im_patcher.stop()
        super(TestPlugin, self).tearDown()

    def fake_instance(self, *args, **kwargs):
        return {
            'nova_instance_id': str(uuid.uuid4()),
            'ip_address': '10.11.12.13'
        }

    def fake_deviceinstance(self):
        return {
            'name': 'fake-name',
            'host': 'fake-host',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password',
            'protocol': 'http',
            'port': 12345
        }

    def blank(self, resource):
        attr_map = resources.RESOURCE_ATTRIBUTE_MAP[resource]
        return dict((k, attr_map[k]['default'])
                    for k in attr_map
                    if 'default' in attr_map[k]
                    and not callable(attr_map[k]['default'])
                    and attr_map[k]['is_visible'])

    def default_options(self):
        return self.blank(resources.RESOURCES)

    def test_create_a10_device_instance(self):
        instance = {}
        context = self.context()
        result = self.plugin.create_a10_device_instance(context, self.envelope(instance))
        self.assertIsNotNone(result['id'])

        expected = self.default_options()
        expected.update(instance)
        expected.update(
            {
                'id': result['id'],
                'nova_instance_id': result['nova_instance_id'],
                'host': result['host'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                'api_version': self.vthunder_defaults['api_version'],
                'username': self.vthunder_defaults['username'],
                'password': self.vthunder_defaults['password'],
                'protocol': self.vthunder_defaults['protocol'],
                'port': self.vthunder_defaults['port'],
                'description': ''
            })

        self.assertEqual(expected, result)

    def test_create_a10_device_instance_options(self):
        instance = self.fake_deviceinstance()
        context = self.context()
        result = self.plugin.create_a10_device_instance(context, self.envelope(instance))
        self.assertIsNotNone(result['id'])

        expected = self.default_options()
        expected.update(instance)
        expected.update(
            {
                'id': result['id'],
                'nova_instance_id': result['nova_instance_id'],
                'host': result['host'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id
            })

        self.assertEqual(expected, result)

    def test_update_a10_device_instance_options(self):
        instance = self.default_options()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_instance(create_context,
                                                               self.envelope(instance))
        self.assertIsNotNone(create_result['id'])

        request = self.fake_deviceinstance()
        context = self.context()
        result = self.plugin.update_a10_device_instance(context,
                                                        create_result['id'],
                                                        self.envelope(request))

        expected = create_result.copy()
        expected.update(request)

        self.assertEqual(expected, result)

    def test_get_a10_device_instance(self):
        instance = self.fake_deviceinstance()
        create_context = self.context()
        create_result = self.plugin.create_a10_device_instance(create_context,
                                                               self.envelope(instance))

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

    def _build_instance(self):
        return {
            "a10_device_instance": {
                "name": "asdf",
                "host": "10.10.42.42",
                "image": "MY_FAKE_IMAGE",
                "flavor": "MY_FAKE_FLAVOR",
                "management_network": "this_network",
                "data_networks": ["that_network"],
            }
        }

    def test_supported_extension_aliases(self):
        sea = self.plugin.supported_extension_aliases
        self.assertEqual([constants.A10_DEVICE_INSTANCE_EXT], sea)

    def test_create_calls_instance_manager(self):
        context = self.context()
        context.session = mock.MagicMock()
        self.target.create_a10_device_instance(context, self._build_instance())
        self.assertTrue(self.instance_manager.create_device_instance.called)

    def test_delete_calls_instance_manager(self):
        context = self.context()
        context.session = mock.MagicMock()
        self.target.delete_a10_device_instance(context, 1)
        delete_call = self.instance_manager.delete_instance
        self.assertTrue(delete_call.called)
