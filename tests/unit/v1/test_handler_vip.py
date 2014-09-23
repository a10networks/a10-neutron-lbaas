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


class TestVIP(test_base.UnitTestBase):

    def fake_vip(self, pers=None):
        h = {
            'tenant_id': 'ten1',
            'id': 'id1',
            'protocol': 'HTTP',
            'admin_state_up': True,
            'address': '1.1.1.1',
            'protocol_port': '80',
            'pool_id': 'pool1',
        }
        if pers:
            h['session_persistence'] = {'type': pers}
        return h.copy()

    def test_create(self):
        self.a.vip.create(None, self.fake_vip())
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('virtual_server.create' in s)
        self.assertTrue('1.1.1.1' in s)
        self.assertTrue('vport.create' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.assertTrue('get_pool' in s)
        self.assertTrue('HTTP' in s)

    def test_create_pers(self):
        self.a.vip.create(None, self.fake_vip('HTTP_COOKIE'))
        s = str(self.a.last_client.mock_calls)
        self.assertTrue("c_pers_name='id1'" in s)

    def test_create_unsupported(self):
        try:
            self.a.vip.create(None, self.fake_vip('APP_COOKIE'))
        except a10_ex.UnsupportedFeature:
            pass

    def test_update(self):
        self.a.vip.update(None, self.fake_vip(), self.fake_vip())
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.assertTrue('get_pool' in s)
        self.assertTrue('HTTP' in s)

    def test_delete(self):
        self.a.vip.delete(None, self.fake_vip())
        self.a.last_client.slb.virtual_server.delete.assert_called_with('id1')

    def test_delete_pers(self):
        self.a.vip.delete(None, self.fake_vip('SOURCE_IP'))
        self.a.last_client.slb.virtual_server.delete.assert_called_with('id1')
        z = self.a.last_client.slb.template.src_ip_persistence.delete
        z.assert_called_with('id1')
