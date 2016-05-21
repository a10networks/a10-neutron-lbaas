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

import sys

import mock

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.tests.unit import test_base

m = mock.Mock()
mock_modules = {
    'a10_neutron_lbaas.vthunder': m,
    'a10_neutron_lbaas.vthunder.instance_manager': m.instance_manager,
    'a10_neutron_lbaas.vthunder.keystone': m.keystone,
}
with mock.patch.dict(sys.modules, mock_modules):
    import a10_neutron_lbaas.plumbing.vthunder_per_tenant as hooks
    reload(hooks)


class TestConfig(object):
    use_database = True
    database_connection = 'http://junk'
    keystone_auth_url = 'http://127.0.0.1:5000/v2.0'
    keystone_version = 2
    plumbing_hooks_class = hooks.VThunderPerTenantPlumbingHooks
    devices = {}
    vthunder = {
        'api_version': '3.0',

        'username': 'admin',
        'password': 'a10',

        'nova_flavor': 'vthunder.small',
        'glance_image': 'ACOS 4.0.3-GA (build 62)',

        'vthunder_tenant_name': 'demo',
        'vthunder_tenant_username': 'demo',
        'vthunder_tenant_password': 'admin',

        'vthunder_management_network': 'mgmt-net',
        'vthunder_data_networks': ['private'],

        'destroy_on_empty': True
    }


class TestPlumbingVThunderPerTenant(test_base.UnitTestBase):

    def setUp(self, **kwargs):
        super(TestPlumbingVThunderPerTenant, self).setUp(
            config=a10_config.A10Config(config=TestConfig))

    def _build_a10_context(self):
        class FakeA10Context(object):
            a10_driver = self.a
            device_cfg = {
                'nova_instance_id': '101'
            }

        return FakeA10Context

    def test_partition_empty_not_shared(self):
        self.assertIsNone(self.a.hooks.partition_empty(
            self._build_a10_context(), None, 'alternate_part_name'))

    def test_partition_empty_not_configured(self):
        self.a.config._vthunder['destroy_on_empty'] = False
        self.assertIsNone(self.a.hooks.partition_empty(
            self._build_a10_context(), None, 'shared'))
        self.a.config._vthunder['destroy_on_empty'] = True

    def test_partition_empty(self):
        z = self.a.hooks.partition_empty(self._build_a10_context(), None, 'shared')
        self.assertIn('delete_instance', str(z))
