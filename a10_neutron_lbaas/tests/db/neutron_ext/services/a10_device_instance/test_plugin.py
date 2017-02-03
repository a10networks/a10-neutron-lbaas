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

from a10_neutron_lbaas.tests.db.neutron_ext.db import test_a10_device_instance

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.services.a10_device_instance.plugin as plugin
import a10_neutron_lbaas.vthunder.instance_manager as instance_manager

import mock


class TestPlugin(test_a10_device_instance.TestA10DeviceInstanceDbMixin):

    def setUp(self):
        super(TestPlugin, self).setUp()
        self._config = a10_config.A10Config()
        self.plugin = plugin.A10DeviceInstancePlugin()
        self.target = self.plugin
        self.instance_manager = mock.MagicMock()
        instance_manager.InstanceManager.from_config = mock.MagicMock(
            return_value=self.instance_manager)
        create_instance_func = lambda x, y: {"a10_device_instance": x}

        self.instance_manager.create_device_instance.side_effect = create_instance_func

    def _build_instance(self):
        rv = {
            "name": "asdf",
            "host": "10.10.42.42",
            "image": "MY_FAKE_IMAGE",
            "flavor": "MY_FAKE_FLAVOR",
            "networks": ["this_network", "that_network"],
        }
        # rv.update(self.vthunder_options())
        rv.update(self.fake_deviceinstance())
        return {"a10_device_instance": rv}

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
