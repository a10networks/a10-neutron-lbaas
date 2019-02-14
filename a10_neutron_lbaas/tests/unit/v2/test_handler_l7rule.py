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


class TestL7Rule(test_base.HandlerTestBase):
    def test_create_l7Rule(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        policy = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                        "http//:google.com", 23)
        rule = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                    'STARTS_WITH', 'testkey', 'testvalue')
        policy.rules = []
        policy.rules.append(rule)
        rule.policy = policy
        self.a.l7rule.create(None, rule)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-l7policy-id-001' in sm)
        self.assertTrue('slb.aflex_policy.create' in sm)

    def test_update_l7Rule(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        policy = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                        "http//:google.com", 23)
        rule = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                    'STARTS_WITH', 'testkey', 'oldvalue')
        policy.rules = []
        policy.rules.append(rule)
        old_rule = rule
        old_rule.policy = policy
        rule = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                    'STARTS_WITH', 'testkey',
                                    'updatedtestvalue')
        policy.rules = []
        policy.rules.append(rule)
        rule.policy = policy
        self.a.l7rule.update(None, old_rule, rule)
        sm = str(self.a.last_client.mock_calls)

        self.assertTrue('fake-l7policy-id-001' in sm)
        self.assertTrue('slb.aflex_policy.create' in sm)
        self.assertTrue('updatedtestvalue' in sm)
        self.assertFalse('oldvalue' in sm)

    def test_delete_l7Rule(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        policy = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                        "http//:google.com", 23)
        rule = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                    'STARTS_WITH', 'testkey', 'testvalue')
        policy.rules = []
        policy.rules.append(rule)
        rule.policy = policy
        self.a.l7rule.delete(None, rule)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-l7policy-id-001' in sm)
        self.assertTrue('slb.aflex_policy.create' in sm)
        self.assertTrue('true' in sm)
        self.assertFalse('testvalue' in sm)

    def test_delete_l7Rule_from_multiple(self):
        lb = fake_objs.FakeLoadBalancer()
        flist = fake_objs.FakeListener('HTTP', 80, pool=None,
                                       loadbalancer=lb)
        flist.loadbalancer_id = "fake-lb-id-001"
        policy = fake_objs.FakeL7Policy(flist, "REDIRECT_TO_URL", None,
                                        "http//:google.com", 23)
        rule1 = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                     'STARTS_WITH', 'testkey', 'oldvalue')
        rule1.id = 'testrule1'
        policy.rules = []
        policy.rules.append(rule1)
        rule1.policy = policy
        self.a.l7rule.create(None, rule1)

        rule2 = fake_objs.FakeL7Rule(policy.id, 'FILE_TYPE',
                                     'STARTS_WITH', 'testkey',
                                     'updatedtestvalue')
        rule2.id = 'testrule2'
        policy.rules.append(rule2)
        rule2.policy = policy
        self.a.l7rule.create(None, rule2)
        self.a.l7rule.delete(None, rule2)
        sm = str(self.a.last_client.mock_calls)
        self.assertTrue('fake-l7policy-id-001' in sm)
        self.assertTrue('slb.aflex_policy.create' in sm)
        self.assertFalse('updatedtestvalue' in sm)
        self.assertTrue('oldvalue' in sm)
