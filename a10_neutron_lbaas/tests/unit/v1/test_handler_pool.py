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

import fake_objs
import test_base


class TestPools(test_base.UnitTestBase):

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

                pool = fake_objs.FakePool(p, m)
                self.a.pool.create(None, pool)

                self.print_mocks()
                (self.a.last_client.slb.service_group.create.
                    assert_called())

                if not saw_exception:
                    n = str(self.a.last_client.mock_calls).index(
                        'slb.service_group.create')
                    self.assertTrue(n >= 0)

    def test_update(self):
        old_pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN')
        self.a.pool.update(None, old_pool, pool)
        self.print_mocks()
        self.a.last_client.slb.service_group.update.assert_called()

    def _test_delete(self, pool):
        self.a.pool.delete(None, pool)
        self.print_mocks()

    def test_delete(self):
        pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        pool.members = [fake_objs.FakeMember()]
        pool.health_monitors_status = [{'monitor_id': 'hm1', "pools": [pool]}]
        self.a.pool.neutron.openstack_driver._pool_get_hm.return_value = fake_objs.FakeHM()

        self._test_delete(pool)

        (self.a.last_client.slb.service_group.delete.
            assert_called_with(pool['id']))

    def test_delete_with_hm_dissociates_hm(self):
        pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        hm = fake_objs.FakeHM("TCP")
        hm.pools.append(fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS'))
        pool.members = [fake_objs.FakeMember()]
        pool.health_monitors_status = [{'monitor_id': 'hm1', "pools": [pool]}]

        self.a.pool.neutron.openstack_driver._pool_get_hm.return_value = hm

        self._test_delete(pool)
        self.a.last_client.slb.service_group.update.assert_called_with(
            "id1",
            health_monitor="",
            health_check_disable=True)

    def test_delete_without_health_monitor(self):
        pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        pool.members = [fake_objs.FakePool()]
        pool.health_monitors_status = []
        self._test_delete(pool)
        (self.a.last_client.slb.service_group.delete.
            assert_called_with(pool.id))

    def test_delete_removes_monitor(self):
        pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        pool.members = [fake_objs.FakeMember()]
        pool.health_monitors_status = [{'monitor_id': "hm1"}]
        self.a.pool.delete(None, pool)
        self.a.last_client.slb.hm.delete.assert_called()

    def test_stats(self):
        pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS')
        z = self.a.pool
        z.neutron.pool_get_tenant_id = lambda x, y: 'hello'
        z._get_vip_id = lambda x, y: '2.2.2.2'
        z.stats(None, pool.id)
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue(s.index('slb.virtual_server.stats') >= 0)
