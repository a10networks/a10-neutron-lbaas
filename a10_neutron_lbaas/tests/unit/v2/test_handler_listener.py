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

import logging
import mock

import fake_objs
import test_base

import a10_neutron_lbaas.a10_exceptions as a10_ex
from a10_neutron_lbaas import constants

LOG = logging.getLogger(__name__)


class TestListeners(test_base.HandlerTestBase):

    def test_create_no_lb(self):
        m = fake_objs.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        try:
            self.a.listener.create(None, m)
        except a10_ex.UnsupportedFeature:
            pass

    def test_create_no_pool(self):
        m = fake_objs.FakeListener('HTTP', 8080, pool=None,
                                   loadbalancer=fake_objs.FakeLoadBalancer())
        self.a.listener.create(None, m)
        self.print_mocks()
        self.assertTrue('create' in str(self.a.last_client.mock_calls))

    def test_create(self):
        admin_states = [True, False]
        persistences = [None, 'SOURCE_IP', 'HTTP_COOKIE', 'APP_COOKIE']
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS']
        lb = fake_objs.FakeLoadBalancer()

        for a in admin_states:
            for pers in persistences:
                for p in protocols:
                    self.a.reset_mocks()

                    pool = fake_objs.FakePool(p, 'ROUND_ROBIN', pers)
                    m = fake_objs.FakeListener(p, 2222, pool=pool,
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
                        if p in ('HTTPS', constants.PROTOCOL_TERMINATED_HTTPS):
                            test_prot = 'TCP'
                        self.assertTrue(test_prot in s)

                    if pers == 'SOURCE_IP':
                        self.assertTrue('s_pers_name=None' not in s)
                        pass
                    elif pers == 'HTTP_COOKIE':
                        self.assertTrue('s_pers=HTTP_COOKIE')
                        self.assertTrue('c_pers_name=None' not in s)
                        pass
                    elif pers == 'APP_COOKIE':
                        self.assertTrue('s_pers=APP_COOKIE')
                        self.assertTrue('c_pers_name=None' not in s)
                        pass
                    else:
                        self.assertTrue('c_pers_name=None' in s)
                        self.assertTrue('s_pers_name=None' in s)

    def test_create_autosnat_false_v21(self):
        self._test_create_autosnat("2.1", False)

    def test_create_autosnat_true_v21(self):
        self._test_create_autosnat("2.1", True)

    def test_create_autosnat_unspecified_v21(self):
        self._test_create_autosnat()

    def test_create_autosnat_false_v30(self):
        self._test_create_autosnat("3.0", False)

    def test_create_autosnat_true_v30(self):
        self._test_create_autosnat("3.0", True)

    def test_create_autosnat_unspecified_v30(self):
        self._test_create_autosnat("3.0")

    def _test_create_autosnat(self, api_ver=None, autosnat=None):
        saw_exception = False

        """
        Due to how the config is pulled in, we can't override the config
        version here and just expect it to work.
        """

        for k, v in self.a.config.get_devices().items():
            v['api_version'] = api_ver
            v['autosnat'] = autosnat

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)

        try:
            self.a.listener.create(None, m)
        except Exception as e:
            saw_exception = True
            raise e

        if not saw_exception:
            s = str(self.a.last_client.mock_calls)
            self.assertIn('vport.create', s)
            self.assertIn('autosnat=%s' % autosnat, s)

    def _test_create_ipinip(self, api_ver="3.0", ip_in_ip=False):
        for k, v in self.a.config.devices.items():
            v['ipinip'] = ip_in_ip
            v['api_version'] = api_ver

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)

        self.a.listener.create(None, m)
        self.print_mocks()

        s = str(self.a.last_client.mock_calls)
        self.assertIn("vport.create", s)
        self.assertIn("ipinip=%s" % ip_in_ip, s)

    def test_create_ip_in_ip_positive_v21(self):
        self._test_create_ipinip(api_ver="2.1", ip_in_ip=True)

    def test_create_ip_in_ip_negative_v21(self):
        self._test_create_ipinip(api_ver="2.1")

    def test_create_ip_in_ip_positive_v30(self):
        self._test_create_ipinip(ip_in_ip=True)

    def test_create_ip_in_ip_negative_v30(self):
        self._test_create_ipinip()

    def test_update_no_lb(self):
        m = fake_objs.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        try:
            self.a.listener.update(None, m, m)
        except a10_ex.UnsupportedFeature:
            pass

    def test_update_no_pool(self):
        m = fake_objs.FakeListener('HTTP', 8080, pool=None,
                                   loadbalancer=fake_objs.FakeLoadBalancer())
        self.a.listener.create(None, m)
        self.assertFalse('update' in str(self.a.last_client.mock_calls))

    def test_update(self):
        pool = fake_objs.FakePool('HTTP', 'ROUND_ROBIN', None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener('HTTP', 2222, pool=pool, loadbalancer=lb)
        pool.listener = m

        self.a.listener.update(None, m, m)

        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTP' in s)

    def test_delete(self):
        pool = fake_objs.FakePool('HTTP', 'ROUND_ROBIN', None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener('HTTP', 2222, pool=pool, loadbalancer=lb)
        pool.listener = m

        self.a.listener.delete(None, m)

        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.delete' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTP' in s)

    def test_delete_removes_bindings(self):
        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN', None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener('TCP', 2222, pool=pool, loadbalancer=lb)
        binding = fake_objs.FakeCertificateBinding(listener_id=m.id)
        pool.listener = m
        bindings = [binding]
        get_bindings_mock = mock.Mock(return_value=bindings)
        self.a.listener.cert_db.get_bindings_for_listener = get_bindings_mock
        self.a.config.use_database = True
        self.a.listener.delete(None, m)
        expected = self.a.listener.cert_db.delete_a10_certificate_binding.call_count
        self.assertEqual(expected, len(bindings))

    def test_delete_no_db_delete_use_database_false(self):
        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN', None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener('TCP', 2222, pool=pool, loadbalancer=lb)
        binding = fake_objs.FakeCertificateBinding(listener_id=m.id)
        pool.listener = m
        bindings = [binding]
        get_bindings_mock = mock.Mock(return_value=bindings)
        self.a.listener.cert_db.get_bindings_for_listener = get_bindings_mock
        self.a.listener.delete(None, m)
        expected = self.a.listener.cert_db.delete_a10_certificate_binding.call_count
        self.assertEqual(expected, 0)

    def _test_create_source_nat_pool(self, source_nat_pool):
        if source_nat_pool:
            for k, v in self.a.config.devices.items():
                v['source_nat_pool'] = source_nat_pool
        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)

        self.a.listener.create(None, m)
        self.print_mocks()

        s = str(self.a.last_client.mock_calls)

        self.assertIn("vport.create", s)

        if source_nat_pool:
            expected = "source_nat_pool='{0}'".format(source_nat_pool)
            self.assertIn(expected, s)
        else:
            self.assertIn("source_nat_pool=None", s)

    def test_create_source_nat_pool_positive(self):
        self._test_create_source_nat_pool("mypool")

    def test_create_source_nat_pool_negative(self):
        self._test_create_source_nat_pool(None)

    def _set_device_config(self, key, value):
        for k, v in self.a.config.devices.items():
            v[key] = value

    def _get_vport_config(self):
        return {
            "gslb-enable": 1
        }

    def test_create_vport_defaults_device(self):
        expected = self._get_vport_config()
        self._set_device_config("vport_defaults", expected)

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)

        self.a.listener.create(None, m)
        self.print_mocks()

        s = str(self.a.last_client.mock_calls)

        self.assertIn("vport.create", s)
        self.assertIn(str(expected), s)

    def test_create_vport_defaults_global(self):
        expected = self.a.config.get_vport_defaults()

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)
        handler = self.a.listener
        handler.create(None, m)
        self.print_mocks()

        s = str(self.a.last_client.mock_calls)

        self.assertIn("vport.create", s)
        self.assertIn(str(expected), s)

    def _test_create_expressions(self, os_name, pattern, expressions=None):
        self.a.config.get_vport_expressions = self._get_expressions_mock
        expressions = expressions or self.a.config.get_vport_expressions()
        expected = expressions.get(pattern, {}).get("json", {})
        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)
        m.name = os_name
        handler = self.a.listener
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("vport.create", s)
        self.assertIn(str(expected), s)

    def test_create_vport_expressions_none(self):
        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)
        handler = self.a.listener
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("vport.create", s)

    def test_create_vport_expressions_match_beginning(self):
        self._test_create_expressions("securelistener", self.EXPR_BEGIN)

    def test_create_vport_expressions_match_end(self):
        self._test_create_expressions("blahweb", self.EXPR_END)

    def test_create_vport_expressions_match_charclass(self):
        self._test_create_expressions("listenerwwwlis", self.EXPR_CLASS)

    def test_create_vport_expressions_nomatch(self):
        self.a.config.get_vport_expressions = self._get_expressions_mock
        expressions = self.a.config.get_vport_expressions()

        expected = expressions[self.EXPR_BEGIN].get("json", {})
        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool,
                                   loadbalancer=lb)
        m.name = "insecurelistener"
        handler = self.a.listener
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("vport.create", s)
        self.assertNotIn(str(expected), s)

    def test_create_vport_expressions_empty(self):
        get_expr_mock = mock.MagicMock()
        get_expr_mock.return_value = {}
        self.a.config.get_vport_expressions = get_expr_mock

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool, loadbalancer=lb)
        m.name = "insecurelistener"
        handler = self.a.listener
        handler.create(None, m)
        # This test should just run without raising any exceptions

    def test_create_vport_expressions_noname(self):
        get_expr_mock = mock.MagicMock()
        get_expr_mock.return_value = {}
        self.a.config.get_vport_expressions = get_expr_mock

        p = 'TCP'
        lb = fake_objs.FakeLoadBalancer()
        pool = fake_objs.FakePool(p, 'ROUND_ROBIN', None)
        m = fake_objs.FakeListener(p, 2222, pool=pool, loadbalancer=lb)
        m.name = None
        handler = self.a.listener
        handler.create(None, m)
        # This test should just run without raising any exceptions
