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
import test_handler_member


class TestPools(test_base.UnitTestBase):
    def fake_hm(self, type):
        hm = {
            'tenant_id': 'tenv1',
            'id': 'abcdef',
            'name': 'abcdef',
            'type': type,
            'delay': '5',
            'timeout': 5,
            'max_retries': '5',
            'pools': [],
        }
        if type in ['HTTP', 'HTTPS']:
            hm['http_method'] = 'GET'
            hm['url_path'] = '/'
            hm['expected_codes'] = '200'
        return hm.copy()

    def fake_pool(self, protocol, method):
        return {
            'tenant_id': 'ten1',
            'id': 'id1',
            'protocol': protocol,
            'lb_method': method,
        }.copy()

    def test_create(self):
        methods = {
            'ROUND_ROBIN':
                self.a.last_client.slb.service_group.ROUND_ROBIN,
            'LEAST_CONNECTIONS':
                self.a.last_client.slb.service_group.LEAST_CONNECTION,
            'SOURCE_IP':
                self.a.last_client.slb.service_group.WEIGHTED_LEAST_CONNECTION,
        }
        protocols = {
            'TCP': self.a.last_client.slb.service_group.TCP,
            'UDP': self.a.last_client.slb.service_group.UDP,
        }

        for p in protocols.keys():
            for m in methods.keys():
                self.a.reset_mocks()
                saw_exception = False

                pool = self.fake_pool(p, m)
                self.a.pool.create(None, pool)

                self.print_mocks()
                (self.a.last_client.slb.service_group.create.
                    assert_called())

                if not saw_exception:
                    n = str(self.a.last_client.mock_calls).index(
                        'slb.service_group.create')
                    self.assertTrue(n >= 0)

    def test_update(self):
        old_pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        pool = self.fake_pool('TCP', 'ROUND_ROBIN')
        self.a.pool.update(None, old_pool, pool)
        self.print_mocks()
        self.a.last_client.slb.service_group.update.assert_called()

    def _test_delete(self, pool):
        self.a.pool.delete(None, pool)
        self.print_mocks()

    def test_delete(self):
        pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        pool['members'] = [test_handler_member._fake_member()]
        pool['health_monitors_status'] = [{'monitor_id': 'hm1', "pools": [pool]}]
        self.a.pool.neutron.openstack_driver._pool_get_hm.return_value = test_base.FakeHM()

        self._test_delete(pool)

        (self.a.last_client.slb.service_group.delete.
            assert_called_with(pool['id']))

    def test_delete_with_hm_dissociates_hm(self):
        pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        hm = self.fake_hm("TCP")
        hm["pools"].append(self.fake_pool('TCP', 'LEAST_CONNECTIONS'))
        pool['members'] = [test_handler_member._fake_member()]
        pool['health_monitors_status'] = [{'monitor_id': 'hm1', "pools": [pool]}]

        self.a.pool.neutron.openstack_driver._pool_get_hm.return_value = hm

        self._test_delete(pool)
        self.a.last_client.slb.service_group.update.assert_called_with(
            "id1",
            health_monitor="",
            health_check_disable=True)

    def test_delete_without_health_monitor(self):
        pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        pool['members'] = [test_handler_member._fake_member()]
        pool['health_monitors_status'] = []
        self._test_delete(pool)
        (self.a.last_client.slb.service_group.delete.
            assert_called_with(pool['id']))

    def test_delete_removes_monitor(self):
        pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        pool['members'] = [test_handler_member._fake_member()]
        pool['health_monitors_status'] = [{'monitor_id': "hm1"}]
        self.a.pool.delete(None, pool)
        self.a.last_client.slb.hm.delete.assert_called()

    def test_stats(self):
        pool = self.fake_pool('TCP', 'LEAST_CONNECTIONS')
        z = self.a.pool
        z.neutron.pool_get_tenant_id = lambda x, y: 'hello'
        z._get_vip_id = lambda x, y: '2.2.2.2'
        z.stats(None, pool['id'])
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue(s.index('slb.virtual_server.stats') >= 0)
