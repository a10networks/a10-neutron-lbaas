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


class FakeHM(test_base.FakeModel):

    def __init__(self, prot, pool=None):
        super(FakeHM, self).__init__()
        self.id = 'fake-hm-id-001'
        self.name = 'hm1'
        self.type = prot
        self.delay = 6
        self.timeout = 7
        self.max_retries = 8
        self.http_method = 'GET'
        self.url_path = '/'
        self.expected_codes = '200'
        self.pool = pool

class TestHM(test_base.UnitTestBase):

    def test_create_ping(self):
        self.a.hm.create(None, FakeHM('PING'))
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.ICMP, 6, 7, 8,
            method=None, url=None, expect_code=None)

    def test_create_tcp(self):
        self.a.hm.create(None, FakeHM('TCP'))
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.TCP, 6, 7, 8,
            method=None, url=None, expect_code=None)

    def test_create_http(self):
        self.a.hm.create(None, FakeHM('HTTP'))
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.HTTP, 6, 7, 8,
            method='GET', url='/', expect_code='200')

    def test_create_https(self):
        self.a.hm.create(None, FakeHM('HTTPS'))
        self.a.openstack_driver.health_monitor.active.assert_called_with(
            None, 'fake-hm-id-001')
        self.a.last_client.slb.hm.create.assert_called_with(
            'fake-hm-id-001', self.a.last_client.slb.hm.HTTPS, 6, 7, 8,
            method='GET', url='/', expect_code='200')


# create http with hm.pool

# update pool with hm.pool
# update pool with hm.pool to empty string (must still call update!)
# update pool with name

# delete unattached hm
# delete attached hm
