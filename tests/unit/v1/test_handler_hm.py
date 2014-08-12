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
        self.print_mocks()
        raise "hellfire"

    def fake_hm(type):
        hm = {
            'tenant_id': 'tenv1',
            'id': 'abcdef',
            'type': type,
            'delay': '5',
            'timeout': 5,
            'max_retries': '5',
        }
        if type in ['HTTP', 'HTTPS']:
            hm['http_method'] = 'GET'
            hm['url_path'] = '/'
            hm['expected_codes'] = '200'
        return hm.copy()

    def test_create_ping(self):
        self.a.create_pool_health_monitor(None, self.fake_hm('PING'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.ICMP, None, None, None)

    def test_create_tcp(self):
        self.a.create_pool_health_monitor(None, self.fake_hm('TCP'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.TCP, None, None, None)

    def test_create_http(self):
        self.a.create_pool_health_monitor(None, self.fake_hm('HTTP'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.HTTP, 'GET', '/', '200')

    def test_create_https(self):
        self.a.create_pool_health_monitor(None, self.fake_hm('HTTPS'), 'p01')
        self.assert_hm(self.a.last_client.slb.hm.HTTPS, 'GET', '/', '200')

    def test_update_tcp(self, m_old=None, m=None):
        if m_old is None:
            m_old = fake_hm('TCP')
        if m is None:
            m = fake_hm('TCP')
        m['delay'] = 20
        self.a.update_pool_health_monitor(None, m_old, m, 'p01')
        self.print_mocks()
        raise "hellfire"

    def test_delete(self):
        self.a.delete_pool_health_monitor(None, self.fake_hm('HTTP'))
        self.print_mocks()
        raise "hellfire"

    # def test_todo(self):
    #     raise "delete, not last assoc"
    #     raise "delete, last assoc"
    #     raise "create, update all pools, 0, 1, N"
    #     raise "update, same"
