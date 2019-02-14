# Copyright 2019, Omkar Telee (omkartelee01), A10 Networks
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

from a10_neutron_lbaas.tests.unit.v2 import fake_objs
from a10_neutron_lbaas.tests.unit.v2 import test_base


class TestL7Policy(test_base.HandlerTestBase):
    def test_create_l7policy(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        m = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                   "http//:google.com", 23)
        self.a.l7policy.create(None, m)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-l7policy-id-001' in sm)

    def test_update_l7policy(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        m = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                   "http//:google.com", 23)
        m_new = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                       "http://youtube.com", 23)
        self.a.l7policy.update(None, m, m_new)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-l7policy-id-001' in sm)

    def test_delete_l7policy(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        m = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                   "http//:google.com", 23)
        self.a.l7policy.delete(None, m)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-listen-id-001' in sm)
