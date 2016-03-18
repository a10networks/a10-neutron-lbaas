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

import mock
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

    def test_create_default_vrid_none_v21(self):
        self._test_create_default_vrid("2.1", None)

    def test_create_default_vrid_set_v21(self):
        self._test_create_default_vrid("2.1", 7)

    def test_create_default_vrid_none_v30(self):
        self._test_create_default_vrid("3.0", None)

    def test_create_default_vrid_set_v30(self):
        self._test_create_default_vrid("3.0", 7)

    def _test_create_default_vrid(self, api_ver=None, default_vrid=None):

        """
        Due to how the config is pulled in, we override the config
        for all of the devices.
        """

        for k, v in self.a.config.devices.items():
            v['api_version'] = api_ver
            v['default_virtual_server_vrid'] = default_vrid

        lb = test_base.FakeLoadBalancer()
        self.a.lb.create(None, lb)

        create = self.a.last_client.slb.virtual_server.create
        create.assert_has_calls([mock.ANY])
        calls = create.call_args_list

        if default_vrid is not None:
            foundVrid = any(
                x.get('axapi_args', {}).get('virtual_server', {}).get('vrid', {}) is default_vrid
                for (_, x) in calls)
            self.assertTrue(
                foundVrid,
                'Expected to find vrid {0} in {1}'.format(default_vrid, str(calls)))
        if default_vrid is None:
            foundVrid = any(
                'vrid' in x.get('axapi_args', {}).get('virtual_server', {})
                for (_, x) in calls)
            self.assertFalse(
                foundVrid,
                'Expected to find no vrid in {0}'.format(str(calls)))

    # def test_create_with_listeners(self):
    #     pool = test_base.FakePool('HTTP', 'ROUND_ROBIN', None)
    #     m = test_base.FakeLoadBalancer()
    #     for x in [1, 2, 3]:
    #         z = test_base.FakeListener('TCP', 2222+x, pool=pool,
    #                                    loadbalancer=m)
    #         m.listeners.append(z)
    #     self.a.lb.create(None, m)
    #     s = str(self.a.last_client.mock_calls)
    #     self.assertTrue('call.slb.virtual_server.create' in s)
    #     self.assertTrue('fake-lb-id-001' in s)
    #     self.assertTrue('5.5.5.5' in s)
    #     self.assertTrue('UP' in s)
    #     self.assertTrue('vport.create' in s)
    #     for x in [1, 2, 3]:
    #         self.assertTrue(str(2222+x) in s)

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

    def test_delete_removes_slb(self):
        m = test_base.FakeLoadBalancer()
        self.a.lb.delete(None, m)

    def test_refresh(self):
        try:
            self.a.lb.refresh(None, test_base.FakeLoadBalancer())
        except a10_ex.UnsupportedFeature:
            pass

    def test_stats(self):
        self.a.lb.stats(None, test_base.FakeLoadBalancer())
        self.print_mocks()
        # self.a.last_client.slb.virtual_server.stats.assert_called_with(
        #     'fake-id-001')
