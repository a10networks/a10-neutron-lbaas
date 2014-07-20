# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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

import test_base

import a10_neutron_lbaas.a10_exceptions as a10_ex


class TestLB(test_base.UnitTestBase):

    def test_create(self):
        m = test_base.FakeLoadBalancer()
        self.a.lb.create(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.create' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('5.5.5.5' in s)
        self.assertTrue('UP' in s)

    def test_create_with_listeners(self):
        pool = test_base.FakePool('HTTP', 'ROUND_ROBIN', None)
        m = test_base.FakeLoadBalancer()
        for x in [1, 2, 3]:
            z = test_base.FakeListener('TCP', 2222+x, pool=pool,
                                       loadbalancer=m)
            m.listeners.append(z)
        self.a.lb.create(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.create' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('5.5.5.5' in s)
        self.assertTrue('UP' in s)
        self.assertTrue('vport.create' in s)
        for x in [1, 2, 3]:
            self.assertTrue(str(2222+x) in s)

    def test_update_down(self):
        m = test_base.FakeLoadBalancer()
        m.admin_state_up = False
        self.a.lb.update(None, m, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.update' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('5.5.5.5' in s)
        self.assertTrue('DOWN' in s)

    def test_delete(self):
        m = test_base.FakeLoadBalancer()
        self.a.lb.delete(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.delete' in s)
        self.assertTrue('fake-lb-id-001' in s)

    def test_refresh(self):
        try:
            self.a.lb.refresh(None, test_base.FakeModel())
        except a10_ex.UnsupportedFeature:
            pass

    def test_stats(self):
        self.a.lb.stats(None, test_base.FakeModel())
        self.print_mocks()
        self.a.last_client.slb.virtual_server.stats.assert_called_with(
            'fake-id-001')
