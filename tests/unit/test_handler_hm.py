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


class TestHM(test_base.UnitTestBase):

    def assert_hm(self, mon_type, method, url, expect_code):
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', mon_type, 6, 7, 8,
            method=method, url=url, expect_code=expect_code)

    def test_create_ping(self):
        self.a.hm.create(None, test_base.FakeHM('PING'))
        self.assert_hm(self.a.last_client.slb.hm.ICMP, None, None, None)

    def test_create_tcp(self):
        self.a.hm.create(None, test_base.FakeHM('TCP'))
        self.assert_hm(self.a.last_client.slb.hm.TCP, None, None, None)

    def test_create_http(self):
        self.a.hm.create(None, test_base.FakeHM('HTTP'))
        self.assert_hm(self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')

    def test_create_https(self):
        self.a.hm.create(None, test_base.FakeHM('HTTPS'))
        self.assert_hm(self.a.last_client.slb.hm.HTTPS, 'GET', '/', '200')

    def test_create_http_with_pool(self):
        m = test_base.FakeHM('HTTP', pool=mock.MagicMock())
        self.a.hm.create(None, m)
        self.assert_hm(self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='fake-hm-id-001')

    def test_update_tcp(self, m_old=None, m=None):
        if m_old is None:
            m_old = test_base.FakeHM('TCP')
        if m is None:
            m = test_base.FakeHM('TCP')
        m.delay = 20
        self.a.hm.update(None, m_old, m)
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.update.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.TCP, 20, 7, 8,
            method=None, url=None, expect_code=None)

    def test_update_tcp_add_pool(self):
        m = test_base.FakeHM('TCP', pool=mock.MagicMock())
        self.test_update_tcp(m=m)
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='fake-hm-id-001')

    def test_update_tcp_delete_pool(self):
        m_old = test_base.FakeHM('TCP', pool=mock.MagicMock())
        self.test_update_tcp(m_old=m_old)
        self.a.last_client.slb.service_group.update.assert_called_with(
            m_old.pool.id, health_monitor='')

    def test_delete(self):
        self.a.hm.delete(None, test_base.FakeHM('HTTP'))
        self.a.openstack_driver.health_monitor.db_delete.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.delete.assert_called_with('fake-hm-id-001')

    def test_delete_with_pool(self):
        m = test_base.FakeHM('TCP', pool=mock.MagicMock())
        self.a.hm.delete(None, m)
        self.a.openstack_driver.health_monitor.db_delete.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='')
        self.a.last_client.slb.hm.delete.assert_called_with('fake-hm-id-001')
