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

import a10_neutron_lbaas.tests.db.neutron_ext.db.test_a10_appliance as test_a10_appliance

import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.services.a10_appliance.plugin as plugin


class TestPlugin(test_a10_appliance.TestA10ApplianceDbMixin):

    def setUp(self):
        super(TestPlugin, self).setUp()
        self.plugin = plugin.A10AppliancePlugin()

    def test_supported_extension_aliases(self):
        sea = self.plugin.supported_extension_aliases
        self.assertEqual([constants.A10_APPLIANCE_EXT], sea)
