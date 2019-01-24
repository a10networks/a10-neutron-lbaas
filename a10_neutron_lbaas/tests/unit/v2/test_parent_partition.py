# Copyright 2019, A10 Networks
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

import a10_neutron_lbaas.v2.v2_context as a10
import mock

from a10_neutron_lbaas.tests.unit.v2 import fake_objs
from a10_neutron_lbaas.tests.unit.v2 import test_base


class TestA10PartitionKey(test_base.UnitTestBase):
    def _build_openstack_context(self):
        admin_context = {
            "tenant_id": "admin"
        }

        return mock.Mock(get_admin_context=mock.Mock(return_value=admin_context))

    def setUp(self, **kwargs):
        super(TestA10PartitionKey, self).setUp(**kwargs)
        self.handler = self.a.pool
        self.ctx = self._build_openstack_context()
        self.m = fake_objs.FakeLoadBalancer()

    def test_use_parent(self):
        fake_keystone = mock.MagicMock()
        fake_keystone.client.projects.get = mock.MagicMock(
            return_value=fake_objs.FakeKeystoneClient("brick"))
        a10.a10_context.keystone_helpers.KeystoneFromContext = mock.MagicMock(
            return_value=fake_keystone)

        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_key, "brick")

    def test_use_parent_no_parent(self):
        fake_keystone = mock.MagicMock()
        fake_keystone.client.projects.get = mock.MagicMock(
            return_value=fake_objs.FakeKeystoneClient())
        a10.a10_context.keystone_helpers.KeystoneFromContext = mock.MagicMock(
            return_value=fake_keystone)

        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_key, "get-off-my-lawn")
