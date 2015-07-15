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
import test_base

import a10_neutron_lbaas.a10_exceptions as a10_ex
import neutron_lbaas.services.loadbalancer.constants as lbaas_const


LOG = logging.getLogger(__name__)


class TestListenersTerminatedHTTPS(test_base.UnitTestBase):

    def test_update_no_lb(self):
        m = test_base.FakeListener('TCP', 2222, pool=mock.MagicMock(),
                                   loadbalancer=None)
        try:
            self.a.listener.update(None, m, m)
        except a10_ex.UnsupportedFeature:
            pass

    def test_update_no_pool(self):
        m = test_base.FakeListener('HTTP', 8080, pool=None,
                                   loadbalancer=test_base.FakeLoadBalancer())
        self.a.listener.create(None, m)
        self.assertFalse('update' in str(self.a.last_client.mock_calls))

    def test_update(self):
        pool = test_base.FakePool(lbaas_const.PROTOCOL_TERMINATED_HTTPS,
                                  lbaas_const.LB_METHOD_ROUND_ROBIN, None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener(lbaas_const.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        certmgr = FakeCertManager()

        self.a.barbican_client = certmgr
        # self.a.listener.set_certmgr(certmgr)

        pool.listener = m

        self.a.listener.update(None, m, m)

        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTPS' in s)

    def test_delete(self):
        pool = test_base.FakePool(lbaas_const.PROTOCOL_TERMINATED_HTTPS,
                                  lbaas_const.LB_METHOD_ROUND_ROBIN, None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener(lbaas_const.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)

        pool.listener = m

        self.a.listener.delete(None, m)

        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        LOG.debug("DELETE RESULT %s" % s)
        self.assertTrue('vport.delete' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('fake-listen-id-001' in s)
        self.assertTrue('port=2222' in s)
        self.assertTrue('HTTPS' in s)

    def test_create_protocol_terminated_https(self):
        pool = test_base.FakePool(lbaas_const.PROTOCOL_TERMINATED_HTTPS,
                                  lbaas_const.LB_METHOD_ROUND_ROBIN, None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener(lbaas_const.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        pool.listener = m
        certmgr = FakeCertManager()

        self.a.barbican_client = certmgr
        self.a.listener.create(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('HTTPS' in s)

    @mock.patch('a10_neutron_lbaas.v2.handler_listener.certwrapper')
    def test_barbican_client_not_null(self, certmgr):
        self.a.listener.barbican_client = None
        pool = test_base.FakePool(lbaas_const.PROTOCOL_TERMINATED_HTTPS,
                                  lbaas_const.LB_METHOD_ROUND_ROBIN, None)
        lb = test_base.FakeLoadBalancer()
        m = test_base.FakeListener(lbaas_const.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        pool.listener = m
        # certmgr = FakeCertManager()
        import pdb
        pdb.set_trace()
        self.a.listener.create(None, m)
        self.assertTrue(self.a.listener.barbican_client is not None)

        self.assertTrue(True)


class FakeCertManager(object):
    def __init__(self):
        self.get_private_key_value = ""
        self.get_certificate_value = ""
        self.get_private_key_passphrase_value = ""
        self.container_name = "tls-container"
        self.set_mocks()

    def set_mocks(self):
        self.mock_cert = mock.Mock(return_value=self.get_private_key_value)
        self.mock_key = mock.Mock(return_value=self.get_private_key_value)
        self.mock_passphrase = mock.Mock(return_value=self.get_private_key_passphrase_value)
        self.mock_cert_container = mock.Mock()
        self.mock_cert_container.configure_mock(name=self.container_name)

        self.mock_certificate_result = mock.Mock(return_value=mock.Mock(
                                                 get_certificate=self.mock_cert,
                                                 get_private_key=self.mock_key,
                                                 get_private_key_passphrase=self.mock_passphrase,
                                                 _cert_container=self.mock_cert_container))

        self.get_certificate = self.mock_certificate_result

    def set_private_key(self, value):
        self.get_private_key_value = value

    def set_certificate(self, value):
        self.get_certificate_value = value

    def set_private_key_passphrase(self, value):
        self.get_private_key_passphrase_value = value
