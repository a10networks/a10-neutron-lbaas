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

import a10_neutron_lbaas.a10_exceptions as a10_ex


class TestListeners(test_base.UnitTestBase):

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

                    pool = test_base.FakePool(p, 'ROUND_ROBIN', pers)
                    m = test_base.FakeListener(p, 2222, pool=pool,
                                               loadbalancer=lb)
                    pool.listener = m
                    saw_exception = False

                    try:
                        self.a.listener.create(None, m)
                    except a10_ex.UnsupportedFeature as e:
                        if pers == 'APP_COOKIE':
                            saw_exception = True
                        else:
                            raise e

                    self.print_mocks()

                    if not saw_exception:
                        s = str(self.a.last_client.mock_calls)
                        self.assertTrue('vport.create' in s)
                        self.assertTrue('fake-lb-id-001' in s)
                        self.assertTrue('fake-listen-id-001' in s)
                        self.assertTrue('port=2222' in s)
                        test_prot = p
                        if p == 'HTTPS':
                            test_prot = 'TCP'
                        self.assertTrue(test_prot in s)

                    if pers == 'SOURCE_IP':
                        self.assertTrue('s_pers_name=None' not in s)
                        pass
                    elif pers == 'HTTP_COOKIE':
                        self.assertTrue('c_pers_name=None' not in s)
                        pass
                    elif pers == 'APP_COOKIE':
                        self.assertTrue(saw_exception)
                    else:
                        self.assertTrue('c_pers_name=None' in s)
                        self.assertTrue('s_pers_name=None' in s)

    def test_update_no_lb(self):
        m = test_base.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        self.a.listener.update(None, m, m)
        self.assertFalse('update' in str(self.a.last_client.mock_calls))

    def test_update_no_pool(self):
        m = test_base.FakeListener('HTTP', 8080, pool=None,
                                   loadbalancer=test_base.FakeLoadBalancer())
        self.a.listener.create(None, m)
        self.assertFalse('update' in str(self.a.last_client.mock_calls))

    def test_update(self):
        pool = test_base.FakePool('HTTP', 'ROUND_ROBIN', None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener('HTTP', 2222, pool=pool, loadbalancer=lb)
        pool.listener = m

        self.a.listener.update(None, m, m)

        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTP' in s)

    def test_delete_no_lb(self):
        m = test_base.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        self.a.listener.delete(None, m)
        self.assertFalse('delete' in str(self.a.last_client.mock_calls))

    def test_delete(self):
        pool = test_base.FakePool('HTTP', 'ROUND_ROBIN', None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener('HTTP', 2222, pool=pool, loadbalancer=lb)
        pool.listener = m

        self.a.listener.delete(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.delete' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTP' in s)
