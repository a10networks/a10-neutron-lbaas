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

import fake_objs
import test_base


class TestHM(test_base.UnitTestBase):

    def assert_hm(self, model, mon_type, method, url, expect_code):
        self.a.openstack_driver.health_monitor.successful_completion.assert_called_with(
            None, model)
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', mon_type, 7, 7, 8,
            method=method, url=url, expect_code=expect_code, axapi_args={})

    def assert_create_sets_delay_timeout(self, model, mon_type, method, url, expect_code):
        model.timeout = 10
        model.delay = 6
        self.a.openstack_driver.health_monitor.successful_completion.assert_called_with(
            None, model)
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', mon_type, model.delay, model.timeout, 8,
            method=method, url=url, expect_code=expect_code, axapi_args={})

    def test_create_ping(self):
        m = fake_objs.FakeHM('PING')
        self.a.hm.create(None, m)
        self.assert_hm(m, self.a.last_client.slb.hm.ICMP, None, None, None)

    def test_create_tcp(self):
        m = fake_objs.FakeHM('TCP')
        self.a.hm.create(None, m)
        self.print_mocks()
        self.assert_hm(m, self.a.last_client.slb.hm.TCP, None, None, None)

    def test_create_http(self):
        m = fake_objs.FakeHM('HTTP')
        self.a.hm.create(None, m)
        self.assert_hm(m, self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')

    def test_create_https(self):
        m = fake_objs.FakeHM('HTTPS')
        self.a.hm.create(None, m)
        self.assert_hm(m, self.a.last_client.slb.hm.HTTPS, 'GET', '/', '200')

    def test_create_http_with_pool(self):
        m = fake_objs.FakeHM('HTTP', pool=mock.MagicMock())
        self.a.hm.create(None, m)
        self.assert_hm(m, self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='fake-hm-id-001', health_check_disable=False)

    def test_update_tcp(self, m_old=None, m=None):
        if m_old is None:
            m_old = fake_objs.FakeHM('TCP')
        if m is None:
            m = fake_objs.FakeHM('TCP')
        m.delay = 20
        self.a.hm.update(None, m_old, m)
        self.a.openstack_driver.health_monitor.successful_completion.assert_called_with(
            None, m)
        self.a.last_client.slb.hm.update.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.TCP, 20, 7, 8,
            method=None, url=None, expect_code=None, axapi_args={})

    def test_update_tcp_add_pool(self):
        m = fake_objs.FakeHM('TCP', pool=mock.MagicMock())
        self.test_update_tcp(m=m)
        self.print_mocks()
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='fake-hm-id-001', health_check_disable=False)

    def test_update_tcp_delete_pool(self):
        m_old = fake_objs.FakeHM('TCP', pool=mock.MagicMock())
        self.test_update_tcp(m_old=m_old)
        self.print_mocks()
        self.a.last_client.slb.service_group.update.assert_called_with(
            m_old.pool.id, health_monitor='', health_check_disable=True)

    def test_delete(self):
        m = fake_objs.FakeHM('HTTP')
        self.a.hm.tenant_id = "tenant-id"
        self.a.hm.delete(None, m)
        self.a.openstack_driver.health_monitor.successful_completion.assert_called_with(
            None, m, delete=True)
        self.a.last_client.slb.hm.delete.assert_called_with('fake-hm-id-001')

    def test_delete_with_pool(self):
        m = fake_objs.FakeHM('TCP', pool=mock.MagicMock())
        self.a.hm.delete(None, m)
        self.a.openstack_driver.health_monitor.successful_completion.assert_called_with(
            None, m, delete=True)
        self.a.last_client.slb.service_group.update.assert_called_with(
            m.pool.id, health_monitor='', health_check_disable=True)
        self.a.last_client.slb.hm.delete.assert_called_with('fake-hm-id-001')
