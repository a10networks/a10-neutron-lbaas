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


class TestListeners(test_base.UnitTestBase):

    def test_sanity(self):
        pass

    def test_create_no_lb(self):
        m = test_base.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        self.a.listener.create(None, m)
        self.assertFalse('create' in str(self.a.last_client.mock_calls))

    def test_create_no_pool(self):
        m = test_base.FakeListener('HTTP', 8080, pool=None,
                                   loadbalancer=test_base.FakeLoadBalancer())
        self.a.listener.create(None, m)
        self.assertFalse('create' in str(self.a.last_client.mock_calls))

    def test_create(self):
        admin_states = [True, False]
        persistences = [None, 'SOURCE_IP', 'HTTP_COOKIE', 'APP_COOKIE']
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS']
        lb = test_base.FakeLoadBalancer()

        for a in admin_states:
            for pers in persistences:
                for p in protocols:
                    self.a.reset_mocks()
                    print a, " ", pers, " ", p
                    pool = test_base.FakePool(p, 'ROUND_ROBIN', pers)
                    m = test_base.FakeListener(p, 2222, pool=pool,
                                               loadbalancer=lb)
                    pool.listener = m
                    self.a.listener.create(None, m)
                    self.print_mocks()
                    # app cookie should bomb!

        raise "hellfire"

# create matrix
#   up and down
#   3 pers
#   protocols

# update with no lb
# update vanilla

# delete with no lb
# delete vanilla
