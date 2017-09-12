# Copyright 2015 A10 Networks
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


class TestListenersTerminatedHTTPS(test_base.UnitTestBase):

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
        pool = fake_objs.FakePool(constants.PROTOCOL_TERMINATED_HTTPS,
                                  constants.LB_METHOD_ROUND_ROBIN, None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener(constants.PROTOCOL_TERMINATED_HTTPS, 2222,
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
        pool = fake_objs.FakePool(constants.PROTOCOL_TERMINATED_HTTPS,
                                  constants.LB_METHOD_ROUND_ROBIN, None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener(constants.PROTOCOL_TERMINATED_HTTPS, 2222,
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
        pool = fake_objs.FakePool(constants.PROTOCOL_TERMINATED_HTTPS,
                                  constants.LB_METHOD_ROUND_ROBIN, None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener(constants.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        m.default_tls_container_id = "CONTAINERID"
        pool.listener = m

        certmgr = FakeCertManager()

        self.a.barbican_client = certmgr
        self.a.listener.create(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('HTTPS' in s)

    @mock.patch('a10_neutron_lbaas.v2.handler_listener.certwrapper')
    def test_barbican_client_not_null(self, certmgr):
        """This tests that the barbican_client dependency is always there."""
        handler = self.a.listener

        pool = fake_objs.FakePool(constants.PROTOCOL_TERMINATED_HTTPS,
                                  constants.LB_METHOD_ROUND_ROBIN, None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener(constants.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        pool.listener = m
        handler.create(None, m)
        self.assertTrue(handler.barbican_client is not None)

    def _tls_container_shared(self):
        certmgr = FakeCertManager()
        certmgr.certificate = "CERTDATA"
        certmgr.private_key = "PRIVATEKEY"
        certmgr.private_key_passphrase = "SECRETPASSWORD"

        self.a.barbican_client = certmgr
        handler = self.a.listener

        pool = fake_objs.FakePool(constants.PROTOCOL_TERMINATED_HTTPS,
                                  constants.LB_METHOD_ROUND_ROBIN, None)
        lb = fake_objs.FakeLoadBalancer()
        m = fake_objs.FakeListener(constants.PROTOCOL_TERMINATED_HTTPS, 2222,
                                   pool=pool, loadbalancer=lb)
        return (certmgr, m, pool, handler)

    def test_create_tls_container_positive(self):
        """Test that cert data is passed to handler when data is available"""
        certmgr, listener, pool, handler = self._tls_container_shared()
        listener.default_tls_container_id = "CONTAINERID"

        pool.listener = listener

        handler.create(None, listener)
        s = str(self.a.last_client.mock_calls)

        self.assertIn(certmgr.certificate, s)
        self.assertIn(certmgr.private_key, s)
        self.assertIn(certmgr.private_key_passphrase, s)

    def test_create_tls_container_negative(self):
        """Test that cert data is not passed to handler"""

        certmgr, listener, pool, handler = self._tls_container_shared()
        listener.default_tls_container_id = None

        pool.listener = listener
        handler.create(None, listener)
        s = str(self.a.last_client.mock_calls)
        self.assertFalse("cert=" in s)
        self.assertFalse("key=" in s)


class FakeCertManager(object):

    def __init__(self):
        self.private_key = ""
        self.certificate = ""
        self.private_key_passphrase = ""
        self.container_name = "tls-container"

        self.mock_cert_container = mock.Mock()
        self.mock_cert_container.configure_mock(name=self.container_name)

        self.mock_certificate = mock.Mock(
            get_certificate=lambda: self.certificate,
            get_private_key=lambda: self.private_key,
            get_private_key_passphrase=lambda: self.private_key_passphrase,
            _cert_container=self.mock_cert_container)

    def get_certificate(self, container_id, project_id=None, **kwargs):

        # project_id is needed to call a CertManager in Mitaka and later
        if project_id is None:
            raise Exception("project_id is required")

        return self.mock_certificate
