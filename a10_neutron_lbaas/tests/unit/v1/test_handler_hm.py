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


class TestHM(test_base.UnitTestBase):

    def assert_hm(self, mon_type, method, url, expect_code):
        self.print_mocks()
        self.a.last_client.slb.hm.create.assert_called_with(
            'hm01', mon_type, '5', 5, '5',
            url=url, method=method, expect_code=expect_code,
            axapi_args={})

    def test_create_ping(self):
        self.a.hm.create(None, fake_objs.FakeHM('PING'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.ICMP, None, None, None)
        pool_name = self.a.hm._pool_name(None, 'p01')
        self.a.last_client.slb.service_group.update.assert_called_with(
            pool_name, health_monitor='hm01')

    def test_create_tcp(self):
        hm = fake_objs.FakeHM('TCP')
        hm.pools = [{'pool_id': 'p02'}, {'pool_id': 'p01'}]
        self.a.hm.create(None, hm, 'p01')
        self.assert_hm(self.a.last_client.slb.hm.TCP, None, None, None)
        pool_name = self.a.hm._pool_name(None, 'p02')
        self.a.last_client.slb.service_group.update.assert_called_with(
            pool_name, health_monitor='hm01')

    def test_create_http(self):
        self.a.hm.create(None, fake_objs.FakeHM('HTTP'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')
        pool_name = self.a.hm._pool_name(None, 'p01')
        self.a.last_client.slb.service_group.update.assert_called_with(
            pool_name, health_monitor='hm01')

    def test_create_https(self):
        self.a.hm.create(None, fake_objs.FakeHM('HTTPS'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.HTTPS, 'GET', '/', '200')
        pool_name = self.a.hm._pool_name(None, 'p01')
        self.a.last_client.slb.service_group.update.assert_called_with(
            pool_name, health_monitor='hm01')

    def test_update_tcp(self, m_old=None, m=None):
        if m_old is None:
            m_old = fake_objs.FakeHM('TCP')
        if m is None:
            m = fake_objs.FakeHM('TCP')
        m.delay = 20
        self.a.hm.update(None, m_old, m, 'p01')
        self.a.last_client.slb.hm.update.assert_called_with(
            'hm01',
            self.a.last_client.slb.hm.TCP, 20, 5, '5',
            url=None, method=None, expect_code=None,
            axapi_args={})

    def test_delete(self):
        expected = fake_objs.FakePool()
        fakehm = fake_objs.FakeHM('HTTP')
        fakehm.tenant_id = 'tenv1'
        fakehm.id = 'fedcba'
        fakehm.pools.append(expected)

        self.a.hm.openstack_driver.plugin.get_pool.return_value = expected
        self.a.hm.openstack_driver._hm_binding_count.return_value = 1

        self.a.hm.delete(None, fakehm, 'p01')
        self.a.last_client.slb.hm.delete.assert_called_with(fakehm.id)

    def test_delete_updates_pool_health_monitor(self):
        expected = fake_objs.FakePool()
        fakehm = fake_objs.FakeHM('HTTP')
        fakehm.tenant_id = 'tenv1'
        fakehm.id = 'fedcba'
        fakehm.pools = []
        fakehm.pools.append(expected)

        self.a.hm.openstack_driver._pool_get_hm.return_value = fakehm
        self.a.hm.openstack_driver.plugin.get_pool.return_value = expected
        self.a.hm.openstack_driver._hm_binding_count.return_value = 1

        pool_name = self.a.hm._pool_name(None, 'p01')
        self.a.hm.delete(None, fakehm, 'p01')

        self.a.last_client.slb.service_group.update.assert_called_with(
            pool_name, health_monitor='', health_check_disable=True)

    def test_dissociate_calls_service_group_update(self):
        fake_pool = fake_objs.FakePool()
        fake_hm = fake_objs.FakeHM('HTTP')
        fake_hm.id = "id1"
        fake_hm.pools = []
        fake_hm.pools.append(fake_pool)
        fake_hm.tenant_id = "tenv1"

        self.a.hm.dissociate(self.a.last_client, None, fake_hm, fake_pool.id)
        self.a.last_client.slb.service_group.update.assert_called(
            fake_pool.id, health_monitor="", health_check_disable=True)

    def test_dissociate_calls_hm_delete(self):
        fake_pool = fake_objs.FakePool()
        fake_hm = fake_objs.FakeHM('HTTP')
        fake_pool.health_monitor_status = [{"monitor_id": fake_hm.id}]
        fake_hm.id = "id1"
        fake_hm.pools = []
        fake_hm.pools.append(fake_pool)
        fake_hm.tenant_id = "tenv1"

        self.a.hm.dissociate(self.a.last_client, None, fake_hm, fake_pool.id)
        self.a.last_client.hm.service_group.delete.assert_called(self.a.hm._meta_name(fake_hm))
