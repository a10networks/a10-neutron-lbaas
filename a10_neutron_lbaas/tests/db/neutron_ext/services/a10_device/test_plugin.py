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
from mock import patch
import uuid

import a10_openstack_lib.resources.a10_device as resources

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.neutron_ext.common.constants as constants
from a10_neutron_lbaas.neutron_ext.extensions import a10Device
import a10_neutron_lbaas.neutron_ext.services.a10_device.plugin as plugin
from a10_neutron_lbaas.tests.db import fake_obj
from a10_neutron_lbaas.tests.db.neutron_ext.db import test_a10_device

plugin_path = "a10_neutron_lbaas.neutron_ext.services.a10_device.plugin"


class TestPlugin(test_a10_device.TestA10DevicePluginBase):

    def setUp(self):
        super(TestPlugin, self).setUp()
        self.plugin = plugin.A10DevicePlugin()
        self.target = self.plugin

        self.maxDiff = None

        self.instance_manager = mock.Mock()
        self.instance_manager.create_device_instance.side_effect = self.fake_instance

        self.vthunder_defaults = a10_config.A10Config().get_vthunder_config()

        self._im_patcher = mock.patch(
            'a10_neutron_lbaas.vthunder.instance_manager.InstanceManager.from_config',
            return_value=self.instance_manager)
        self._im_patcher.start()

    def tearDown(self):
        self._im_patcher.stop()
        super(TestPlugin, self).tearDown()

    def test_supported_extension_aliases(self):
        sea = self.plugin.supported_extension_aliases
        self.assertEqual([constants.A10_DEVICE_EXT], sea)

    def fake_device(self):
        return fake_obj.FakeA10Device()

    def fake_vthunder(self):
        return fake_obj.FakeA10vThunder()

    def fake_instance(self, *args, **kwargs):
        return {
            'nova_instance_id': str(uuid.uuid4()),
            'ip_address': '10.11.12.13'
        }

    def fake_device_basic_config(self):
        return {
            'name': 'fake-name',
            'host': 'fake-host',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password',
            'protocol': 'https',
            'port': '12345'
        }

    def _build_instance(self):
        return {
            'a10_vthunder': {
                'name': 'asdf',
                'host': '10.10.42.42',
                'username': 'fake-username',
                'password': 'fake-password',
                'api_version': 'fake-version',
                'image': 'MY_FAKE_IMAGE',
                'flavor': 'MY_FAKE_FLAVOR',
                'management_network': 'this_network',
                'data_networks': ['that_network'],
            }
        }

    def blank(self, resource):
        attr_map = resources.RESOURCE_ATTRIBUTE_MAP[resource]
        return dict((k, attr_map[k]['default'])
                    for k in attr_map
                    if 'default' in attr_map[k]
                    and not callable(attr_map[k]['default'])
                    and attr_map[k]['is_visible'])

    def vthunder_default_options(self):
        return self.blank(resources.VTHUNDERS)

    def device_default_options(self):
        return self.blank(resources.DEVICES)

    def devcice_key_default_options(self):
        return self.blank(resources.DEVICE_KEYS)

    def device_value_default_options(self):
        return self.blank(resources.DEVICE_VALUES)

    def test_create_calls_instance_manager(self):
        context = self.context()
        context.session = mock.MagicMock()
        self.target.create_a10_vthunder(context, self._build_instance())
        self.assertTrue(self.instance_manager.create_device_instance.called)

    def test_delete_calls_instance_manager(self):
        context = self.context()
        context.session = mock.MagicMock()
        self.target.delete_a10_vthunder(context, 1)
        delete_call = self.instance_manager.delete_instance
        self.assertTrue(delete_call.called)

    def test_create_a10_vthunder(self):
        instance = self.fake_device_basic_config()
        context = self.context()
        result = self.plugin.create_a10_vthunder(
            context, self.envelope_vthunder(instance))
        self.assertIsNotNone(result['id'])

        result.pop('extra_resources', None)
        expected = self.vthunder_default_options()
        expected.update(
            self.plugin.validate_a10_opts(instance,
                                          'a10_vthunder'))
        expected.pop('a10_opts', None)
        expected.update(
            {
                'id': result['id'],
                'nova_instance_id': result['nova_instance_id'],
                'host': result['host'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                'api_version': 'fake-version',
                'name': 'fake-name',
                'username': 'fake-username',
                'password': 'fake-password',
                'protocol': 'https',
                'port': 12345,
                #'extra_resources': [],
                'description': '',
            })

        self.assertEqual(expected, result)

    def test_create_a10_vthunder_options(self):
        instance = self.fake_vthunder()
        context = self.context()
        result = self.plugin.create_a10_vthunder(
            context, self.envelope_vthunder(instance.__dict__))
        self.assertIsNotNone(result['id'])

        result.pop('extra_resources', None)
        expected = self.vthunder_default_options()
        # Convert a10_opts dict to flat device record ready to insert into db
        expected.update(
            self.plugin.a10_device_body_defaults(instance.__dict__,
                                                 context.tenant_id,
                                                 result['id']))
        expected.pop('a10_opts', None)
        expected.update(
            {
                'id': result['id'],
                'nova_instance_id': result['nova_instance_id'],
                'host': result['host'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                #'extra_resources': [],

            })
        self.assertEqual(expected, result)

    def test_update_a10_vthunder_options(self):
        instance = self.fake_vthunder()
        create_context = self.context()
        create_result = self.plugin.create_a10_vthunder(create_context,
                                                        self.envelope_vthunder(instance.__dict__))
        self.assertIsNotNone(create_result['id'])

        request = self.fake_device_basic_config()
        context = self.context()
        result = self.plugin.update_a10_vthunder(context,
                                                 create_result['id'],
                                                 self.envelope_vthunder(request))

        expected = create_result.copy()
        expected.update(request)
        del expected['extra_resources']

        self.assertEqual(expected, result)

    def test_get_a10_vthunder(self):
        instance = self.fake_vthunder()
        create_context = self.context()
        create_result = self.plugin.create_a10_vthunder(
            create_context, self.envelope_vthunder(instance.__dict__))

        context = self.context()
        result = self.plugin.get_a10_vthunder(context, create_result['id'])

        del create_result['extra_resources']
        self.assertEqual(create_result, result[0])

    def test_get_a10_vthunder_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Device.A10DeviceNotFoundError,
            self.plugin.get_a10_device,
            context,
            'fake-device-id')

    def test_get_a10_vthunders(self):
        instance = self.fake_device_basic_config()
        create_context = self.context()
        create_result = self.plugin.create_a10_vthunder(create_context,
                                                        self.envelope_vthunder(instance))

        context = self.context()
        result = self.plugin.get_a10_vthunders(context)

        del create_result['extra_resources']
        self.assertEqual([create_result], result)

    def test_create_a10_device(self):
        device = self.fake_device()
        context = self.context()
        result = self.plugin.create_a10_device(
            context, self.envelope_device(device.__dict__))
        self.assertIsNotNone(result['id'])

        result.pop('extra_resources', None)
        expected = {}
        # Convert a10_opts dict to flat device record ready to insert into db
        expected.update(
            self.plugin.a10_device_body_defaults(device.__dict__,
                                                 context.tenant_id,
                                                 result['id'],
                                                 'a10_device'))
        expected.update(
            self.plugin.a10_opts_defaults(
                self.plugin.validate_a10_opts(
                    device.a10_opts, 'a10_device'), 'a10_device'))
        expected.pop('config', None)
        expected.update(
            {
                'id': result['id'],
                'host': result['host'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                'nova_instance_id': None,
                'conn_limit': str(expected['conn_limit']),
                #'extra_resources': []
            })

        self.assertEqual(expected, result)

    def test_update_a10_device_options(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.plugin.create_a10_device(
            create_context, self.envelope_device(device.__dict__))
        self.assertIsNotNone(create_result['id'])

        request = {}
        request.update(
            self.plugin.a10_device_body_defaults(device.__dict__,
                                                 create_context.tenant_id,
                                                 create_result['id']))
        request.pop('config', None)
        request.update({'name': 'shrubbery'})

        context = self.context()
        result = self.plugin.update_a10_device(context,
                                               create_result['id'],
                                               self.envelope_device(request))

        expected = create_result.copy()
        expected.update(request)

        self.assertEqual(expected, result)

    def test_get_a10_device(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.plugin.create_a10_device(create_context,
                                                      self.envelope_device(device.__dict__))

        context = self.context()
        result = self.plugin.get_a10_device(context, create_result['id'])

        del create_result['extra_resources']
        self.assertEqual(create_result, result[0])

    def test_get_a10_device_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Device.A10DeviceNotFoundError,
            self.plugin.get_a10_device,
            context,
            'fake-device-id')

    def test_get_a10_devices(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.plugin.create_a10_device(create_context,
                                                      self.envelope_device(device.__dict__))

        context = self.context()
        result = self.plugin.get_a10_devices(context)

        self.assertEqual([create_result], result)

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.create_a10_device_key")
    def test_create_a10_device_key(self, test_super):
        context = self.context()
        key = fake_obj.FakeA10DeviceKey()

        self.plugin.create_a10_device_key(context, self.envelope_device_key(key.__dict__))
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.get_a10_device_key")
    def test_get_a10_device_key(self, test_super):
        context = self.context()
        self.plugin.get_a10_device_key(context, 'spam&eggs')
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.update_a10_device_key")
    def test_update_a10_device_key(self, test_super):
        context = self.context()
        key = fake_obj.FakeA10DeviceKey()

        self.plugin.update_a10_device_key(context, 'spam&eggs',
                                          self.envelope_device_key(key.__dict__))
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.get_a10_device_keys")
    def test_get_a10_device_keys(self, test_super):
        context = self.context()
        self.plugin.get_a10_device_keys(context)
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.delete_a10_device_key")
    def test_delete_a10_device_key(self, test_super):
        context = self.context()
        self.plugin.delete_a10_device_key(context, 'spam&eggs')
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.create_a10_device_value")
    def test_create_a10_device_value(self, test_super):
        context = self.context()
        value = fake_obj.FakeA10DeviceValue('spam&eggs', 'shrubbery')

        self.plugin.create_a10_device_value(context, self.envelope_device_value(value.__dict__))
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.get_a10_device_value")
    def test_get_a10_device_value(self, test_super):
        context = self.context()
        self.plugin.get_a10_device_value(context, 'spam&eggs')
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.update_a10_device_value")
    def test_update_a10_device_value(self, test_super):
        context = self.context()
        value = fake_obj.FakeA10DeviceValue('spam&eggs', 'shrubbery')

        self.plugin.update_a10_device_value(
            context, value.key_id, value.associated_obj_id, 'New-Fake-Value')
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.get_a10_device_values")
    def test_get_a10_device_values(self, test_super):
        context = self.context()
        self.plugin.get_a10_device_values(context)
        test_super.assert_called()

    @patch(plugin_path + ".a10_device.A10DeviceDbMixin.delete_a10_device_value")
    def test_delete_a10_device_value(self, test_super):
        context = self.context()
        self.plugin.delete_a10_device_value(context, 'spam&eggs')
        test_super.assert_called()
