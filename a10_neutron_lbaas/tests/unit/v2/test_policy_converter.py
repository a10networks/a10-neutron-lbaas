# Copyright 2019, Doug Wiegley (dougwig), A10 Networks
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

from a10_neutron_lbaas.v2.policy import PolicyUtil

from a10_neutron_lbaas.tests.unit.v2 import fake_objs
from a10_neutron_lbaas.tests.unit.v2 import test_base


class TestPolicy(test_base.HandlerTestBase):
    def test_create_with_no_rules_action_REDIRECT_TO_URL(self):
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_URL", None,
                                   "http://a10networks.com", 12)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """ when HTTP_REQUEST {
        if { ( true ) } {
        HTTP::redirect http://a10networks.com
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_no_rules_action_REDIRECT_TO_POOL(self):
        pool = fake_objs.FakePool('HTTP', 'ROUND_ROBIN', 'SOURCE_IP')
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_POOL", pool,
                                   None, 12)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """  when HTTP_REQUEST {

        if { ( true ) } {

        pool fake-pool-id-001

        }

        } """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_no_rules_action_REJECT(self):
        m = fake_objs.FakeL7Policy(None, "REJECT", None,
                                   None, 12)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """ when HTTP_REQUEST {

        if { ( true ) } {

        HTTP::close

        }

        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_with_rule_action_REDIRECT_TO_URL(self):
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_URL", None,
                                   "http://a10networks.com", 12)
        r = fake_objs.FakeL7Rule(m.id, 'HOST_NAME',
                                 'STARTS_WITH', None, 'testvalue')
        m.rules = []
        m.rules.append(r)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """ when HTTP_REQUEST {
        if { ([HTTP::host] starts_with "testvalue") } {
        HTTP::redirect http://a10networks.com
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_with_rule_action_REDIRECT_TO_POOL(self):
        pool = fake_objs.FakePool('HTTP', 'ROUND_ROBIN', 'SOURCE_IP')
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_POOL", pool,
                                   None, 12)
        r = fake_objs.FakeL7Rule(m.id, 'FILE_TYPE',
                                 'STARTS_WITH', 'testkey', 'testvalue')
        m.rules = []
        m.rules.append(r)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """    when HTTP_REQUEST {
        if { ([HTTP::uri] ends_with "testvalue") } {
        pool fake-pool-id-001
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_with_rule_action_REJECT(self):
        m = fake_objs.FakeL7Policy(None, "REJECT", None,
                                   None, 12)
        r = fake_objs.FakeL7Rule(m.id, 'COOKIE',
                                 'CONTAINS', 'testkey', 'testvalue')
        m.rules = []
        m.rules.append(r)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """when HTTP_REQUEST {
        if { ([HTTP::cookie testkey] contains "testvalue") } {
        HTTP::close
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_with_multi_rule_action_REDIRECT_TO_URL(self):
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_URL", None,
                                   "http://a10networks.com", 12)
        r1 = fake_objs.FakeL7Rule(m.id, 'HOST_NAME',
                                  'STARTS_WITH', None, 'testvalue')
        r2 = fake_objs.FakeL7Rule(m.id, 'FILE_TYPE',
                                  'STARTS_WITH', 'testkey', 'testvalue')
        r3 = fake_objs.FakeL7Rule(m.id, 'COOKIE',
                                  'CONTAINS', 'testkey', 'testvalue')
        m.rules = []
        m.rules.append(r1)
        m.rules.append(r2)
        m.rules.append(r3)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """  when HTTP_REQUEST {
        if { ([HTTP::host] starts_with "testvalue") and
        ([HTTP::uri] ends_with "testvalue") and
        ([HTTP::cookie testkey] contains "testvalue") } {
        HTTP::redirect http://a10networks.com
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)

    def test_create_with_with_rule_action_REDIRECT_TO_POOL_invert(self):
        pool = fake_objs.FakePool('HTTP', 'ROUND_ROBIN', 'SOURCE_IP')
        m = fake_objs.FakeL7Policy(None, "REDIRECT_TO_POOL", pool,
                                   None, 12)
        r = fake_objs.FakeL7Rule(m.id, 'FILE_TYPE',
                                 'STARTS_WITH', 'testkey', 'testvalue')
        r.invert = True
        m.rules = []
        m.rules.append(r)
        p = PolicyUtil()
        resp = p.createPolicy(m)
        expect_resp = """    when HTTP_REQUEST {
        if { not([HTTP::uri] ends_with "testvalue") } {
        pool fake-pool-id-001
        }
        }
        """
        resp = resp.replace('\n', '').replace(' ', '')
        expect_resp = expect_resp.replace('\n', '').replace(' ', '')
        self.assertEqual(resp, expect_resp)
