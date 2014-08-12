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


class TestVIP(test_base.UnitTestBase):

    def fake_vip(self, pers=None):
        h = {
            'tenant_id': 'ten1',
            'id': 'id1',
            'protocol': protocol,
            'admin_state_up': True,
            'address': '1.1.1.1',
            'port': '80',
            'pool_id': 'pool1',
        }
        if pers:
            h['session_persistence'] = {'type': pers}
        return h.copy()

    def test_create(self):
        self.a.create_vip(None, self.fake_vip())
        self.print_mocks()
        raise "hellfire"

    def test_create_pers(self):
        self.a.create_vip(None, self.fake_vip('HTTP_COOKIE'))
        self.print_mocks()
        raise "hellfire"

    def test_create_unsupported(self):
        self.a.create_vip(None, self.fake_vip('APP_COOKIE'))
        self.print_mocks()
        raise "hellfire"

    def test_update(self):
        self.a.update_vip(None, self.fake_vip(), self.fake_vip())
        self.print_mocks()
        raise "hellfire"

    def test_delete(self):
        self.a.delete_vip(None, self.fake_vip())
        self.print_mocks()
        raise "hellfire"

    def test_delete_pers(self):
        self.a.delete_vip(None, self.fake_vip('SOURCE_IP'))
        self.print_mocks()
        raise "hellfire"
