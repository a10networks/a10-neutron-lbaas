# Copyright (C) 2014-2015, A10 Networks Inc. All rights reserved.
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

import a10_neutron_lbaas
from a10_neutron_lbaas.db.models import a10_certificates as models
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import certificate_db as certs_db
from a10_neutron_lbaas.tests.db import test_base as tbase

import mock
from neutron.plugins.common import constants as nconstants
from neutron.tests.unit.api.v2 import test_base as ntbase

from oslo_log.helpers import logging as logging
from oslo_utils import uuidutils


import os
import os.path


LOG = logging.getLogger(__name__)

_tenant_id = uuidutils.generate_uuid()
_get_path = ntbase._get_path

CERTIFICATE = "a10_certificate"
CERTIFICATES = CERTIFICATE + "s"
CERTIFICATE_BINDING = "a10_certificate_binding"
CERTIFICATE_BINDINGS = CERTIFICATE_BINDING + "s"

CERTIFICATE_EXT = "a10-certificate"


# class CertificateExtensionTestCase(ExtensionTestCase):

#     """Tests a10_openstack.neutron_ext.extensions.Certificates"""

#     def setUp(self):
#         super(CertificateExtensionTestCase, self).setUp()
#         self.plugin = mock.MagicMock()

#         self._setUpExtension(
#             'a10_neutron_lbaas.tests.db.neutron_ext.db.test_certificates.DummyCorePlugin',
#             "", a10Certificate.RESOURCE_ATTRIBUTE_MAP,
#             a10Certificate.A10Certificate, '', supported_extension_aliases='a10-certificate'
#         )

#     def _build_test_binding_collection(self):
#         result = {CERTIFICATE_BINDINGS: []}
#         result[CERTIFICATE_BINDINGS].append(self._build_test_binding(
#             uuidutils.generate_uuid(),
#             uuidutils.generate_uuid(),
#             _tenant_id))
#         result[CERTIFICATE_BINDINGS].append(self._build_test_binding(
#             uuidutils.generate_uuid(),
#             uuidutils.generate_uuid(),
#             _tenant_id))
#         result[CERTIFICATE_BINDINGS].append(self._build_test_binding(
#             uuidutils.generate_uuid(),
#             uuidutils.generate_uuid(),
#             _tenant_id))
#         return result

#     def _build_test_certificate_collection(self):
#         result = {CERTIFICATES: []}

#         result[CERTIFICATES].append(self._build_test_certificate())
#         result[CERTIFICATES].append(self._build_test_certificate(
#             name="Magic Certificate 2"))
#         return result

#     def _build_test_binding(self, certificate_id, vip_id, tenant_id=_tenant_id):
#         result = {'certificate_id': certificate_id,
#                   'vip_id': vip_id}
#         if tenant_id is not None:
#             result['tenant_id'] = tenant_id
#         return result

#     def _build_test_certificate(self, name="Magic Certificate",
#                                 description="Certificate Description",
#                                 cert_data="Super secret certificate data",
#                                 key_data='Key data',
#                                 intermediate_data='Intermediate data',
#                                 tenant_id=_tenant_id,
#                                 password="SecretPassword"):
#         result = {'name': name,
#                   'description': description,
#                   'cert_data': cert_data,
#                   'key_data': key_data,
#                   'intermediate_data': intermediate_data,
#                   'password': password}
#         if tenant_id is not None:
#             result['tenant_id'] = tenant_id
#         return result

#     def test_create_certificate(self):
#         expected = {CERTIFICATE: self._build_test_certificate(_tenant_id)}
#         import pdb
#         pdb.set_trace()
#         # self.plugin.create_a10_certificate = mock.Mock(return_value=expected[CERTIFICATE])

#         self.api.post(_get_path(CERTIFICATES, fmt=self.fmt), self.serialize(expected),
#                       content_type='application/%s' % self.fmt)
#         self.plugin.create_a10_certificate.assert_called_with(mock.ANY, certificate=expected)

#     def test_delete_certificate(self):
#         certificate_id = uuidutils.generate_uuid()
#         self.api.delete(_get_path(CERTIFICATES, id=certificate_id, fmt=self.fmt),
#                         content_type="application/%s" % self.fmt)

#         self.plugin.delete_a10_certificate.assert_called_with(mock.ANY, certificate_id)

#     def test_update_certificate(self):
#         certificate_id = uuidutils.generate_uuid()
#         expected = {CERTIFICATE: self._build_test_certificate(tenant_id=None)}

#         self.plugin.update_a10_certificate = mock.Mock(return_value=expected)
#         self.api.put(_get_path(CERTIFICATES, id=certificate_id, fmt=self.fmt),
#                      self.serialize(expected),
#                      content_type="application/%s" % self.fmt)

#         self.plugin.update_a10_certificate.assert_called_with(mock.ANY,
#                                                               certificate_id,
#                                                               certificate=expected[CERTIFICATE])

#     def test_get_certificate(self):
#         certificate_id = uuidutils.generate_uuid()
#         expected = {CERTIFICATE: self._build_test_certificate()}

#         self.plugin.get_a10_certificate = mock.Mock(return_value=expected[CERTIFICATE])
#         response = self.api.get(_get_path(CERTIFICATES, id=certificate_id, fmt=self.fmt))
#         self.plugin.get_a10_certificate.assert_called_with(
#             mock.ANY, certificate_id, fields=mock.ANY)
#         actual = self.deserialize(response)
#         self.assertEqual(1, len(actual))
#         self.assertEqual(expected, actual)
#         self.assertEqual(expected[CERTIFICATE]['name'], actual[CERTIFICATE]['name'])

#     def test_get_certificates(self):
#         expected = self._build_test_certificate_collection()

#         self.plugin.get_a10_certificates = mock.Mock(return_value=expected[CERTIFICATES])
#         url = _get_path(CERTIFICATES, fmt=self.fmt)
#         response = self.api.get(url)

#         self.plugin.get_a10_certificates.assert_called_with(mock.ANY,
#                                                             fields=mock.ANY,
#                                                             filters=mock.ANY)
#         actual = self.deserialize(response)
#         self.assertEqual(expected[CERTIFICATES], actual[CERTIFICATES])

#     def test_get_certificate_binding(self):
#         binding_id = uuidutils.generate_uuid()
#         certificate_id = uuidutils.generate_uuid()
#         vip_id = uuidutils.generate_uuid()
#         expected = {CERTIFICATE_BINDING: self._build_test_binding(certificate_id, vip_id)}

#         self.plugin.get_a10_certificate_binding = mock.Mock(
#             return_value=expected[CERTIFICATE_BINDING])
#         url = _get_path(CERTIFICATE_BINDINGS, id=binding_id, fmt=self.fmt)
#         response = self.api.get(url)
#         self.plugin.get_a10_certificate_binding.assert_called_with(
#             mock.ANY, binding_id, fields=mock.ANY)
#         actual = self.deserialize(response)
#         self.assertEqual(expected, actual)
#         self.assertEqual("200 OK", response._status)

#     def test_get_certificate_bindings(self):
#         expected = self._build_test_binding_collection()

#         self.plugin.get_a10_certificate_bindings = mock.Mock(
#             return_value=expected[CERTIFICATE_BINDING])
#         url = _get_path(CERTIFICATE_BINDINGS, fmt=self.fmt)
#         result = self.api.get(url)
#         actual = self.deserialize(result)

#         self.plugin.get_a10_certificate_bindings.assert_called_with(mock.ANY,
#                                                                     fields=mock.ANY,
#                                                                     filters=mock.ANY)
#         self.assertEqual(expected, actual)

#     def test_create_certificate_binding(self):
#         certificate_id = uuidutils.generate_uuid()
#         vip_id = uuidutils.generate_uuid()
#         expected = {CERTIFICATE_BINDING: self._build_test_binding(certificate_id, vip_id)}

#         self.plugin.create_a10_certificate_binding = mock.Mock(return_value=expected)
#         url = _get_path(CERTIFICATE_BINDINGS, fmt=self.fmt)
#         self.api.post(url, self.serialize(expected),
#                       content_type='application/%s' % self.fmt)
#         self.plugin.create_a10_certificate_binding.assert_called_with(mock.ANY,
#                                                                       certificate_binding=expected)

#     def test_delete_certificate_binding(self):
#         binding_id = uuidutils.generate_uuid()
#         url = _get_path(CERTIFICATE_BINDINGS, id=binding_id, fmt=self.fmt)
#         self.api.delete(url, content_type="application/%s" % self.fmt)
#         self.plugin.delete_a10_certificate_binding.assert_called_with(mock.ANY, binding_id)


class CertificateDbMixInTestCase(tbase.UnitTestBase):

    """Tests a10_openstack.neutron_ext.db.certificate_db.CertificateManager"""
    _test_name = 'THE CERTIFICATE'
    _test_description = 'THE CERTIFICATE DESCRIBED'
    _test_cert_type = 'Certificate'
    _test_cert_data = 'THE CERT DATA THAT SHOULD BE ENCRYPTED'
    _root_dir = os.path.dirname(os.path.dirname(__file__))
    _etc_dir = os.path.join(_root_dir, 'etc')
    # TODO(mdurrant) Make fake certs and read them in.
    _test_key_data = 'fake key'
    _test_intermediate_data = 'fake intermediate'
    _test_password = 'password'

    # figure out where we're being loaded from
    _base_path = os.path.abspath(a10_neutron_lbaas.__file__)
    _test_path = _base_path[:_base_path.rfind('/')]
    _test_etc_path = os.path.abspath("{0}/tests/etc".format(_test_path))
    _test_conf_path = "{0}/{1}".format(_test_etc_path, 'neutron.conf.test')

    # _test_conf_path =

    def setUp(self):
        super(CertificateDbMixInTestCase, self).setUp()
        self._nm_patcher = mock.patch('neutron.manager.NeutronManager')
        nm = self._nm_patcher.start()
        # nm.get_service_plugins.return_value = {
        #     nconstants.LOADBALANCERV2: mock.MagicMock()
        # }

        self.plugin = certs_db.A10CertificateDbMixin()

    def tearDown(self):
        super(CertificateDbMixInTestCase, self).tearDown()

    def context(self):
        session = self.open_session()
        context = mock.Mock(session=session, tenant_id='fake-tenant-id')
        return context

    def _build_certificate(self, name=_test_name, description=_test_description,
                           cert_data=_test_cert_data, key_data=_test_key_data,
                           intermediate_data=_test_intermediate_data,
                           tenant_id='tenant1', password=_test_password):
        return {'a10_certificate': {'name': name,
                                    'description': description,
                                    'cert_data': cert_data,
                                    'key_data': key_data,
                                    'intermediate_data': intermediate_data,
                                    'password': password,
                                    'tenant_id': tenant_id}}

    def _build_binding(self, certificate_id=None, listener_id=None, tenant_id=None):
        return {'a10_certificate_binding': {'certificate_id': certificate_id,
                                            'listener_id': listener_id,
                                            'tenant_id': tenant_id}}

    def _create_certificate(self, tenant_id='tenant1', ctx=None, description=None):
        if ctx is None:
            ctx = self.context()
        ctx.tenant_id = tenant_id
        certificate = self._build_certificate()
        return self.plugin.create_a10_certificate(ctx, certificate), certificate

    def _create_binding(self, ctx=None, cert_id=None, listener_id=None, tenant_id=_tenant_id):
        if ctx is None:
            ctx = self.context()
        ctx.tenant_id = tenant_id
        binding = self._build_binding(ctx, cert_id, listener_id, tenant_id)

        return self.plugin.create_a10_certificate_listener_binding(ctx, binding), binding

    def test_create_certificate(self, tenant_id="tenant1"):
        ctx = self.context()
        record, request = self._create_certificate(tenant_id)
        res = ctx.session.query(models.Certificate).all()
        self.assertEqual(1, len(res))
        actual = res[0]
        self.assertFalse(actual is None)
        self.assertEqual(self._test_name, actual.name)
        self.assertEqual(self._test_description, actual.description)
        self.assertEqual(self._test_cert_data, actual.cert_data)
        self.assertEqual(self._test_key_data, actual.key_data)
        self.assertEqual(self._test_intermediate_data, actual.intermediate_data)
        self.addCleanup(ctx.session.delete, actual)

    def test_update_certificate(self):
        ctx = self.context()
        cert, certificate = self._create_certificate(ctx=ctx)
        certificate = {'a10_certificate': {'name': 'THE SECOND CERTIFICATE',
                                           'description': 'THE SECOND CERT DESCRIBED',
                                           'cert_data': 'M0re s00p3r s3cr3t d@ta',
                                           'key_data': 'Key data',
                                           'intermediate_data': 'intermediate data',
                                           'password': 'password'}}
        self.plugin.update_a10_certificate(ctx, cert['id'], certificate)
        actual = (ctx.session.query(models.Certificate).filter_by(id=cert['id']).one())
        self.assertEqual('THE SECOND CERTIFICATE', actual.name)
        self.assertEqual('THE SECOND CERT DESCRIBED', actual.description)
        self.assertEqual('M0re s00p3r s3cr3t d@ta', actual.cert_data)

    def test_delete_certificate(self):
        ctx = self.context()
        cert, data = self._create_certificate(ctx=ctx)
        self.plugin.delete_a10_certificate(ctx, cert['id'])
        actual = (ctx.session.query(models.Certificate).filter_by(id=cert['id']).first())
        self.assertTrue(actual is None)

    def test_get_certificate(self):
        ctx = self.context()
        cert, data = self._create_certificate()
        actual = self.plugin.get_a10_certificate(ctx, cert['id'])
        self.assertEqual(cert, actual)

    def test_get_throwsexceptionwhenitdoesntexist(self):
        ctx = self.context()
        self.assertRaises(certs_db.CertificateNotFoundError, self.plugin.get_a10_certificate,
                          (self, ctx, uuidutils.generate_uuid()), None)

    def test_create_certificate_binding(self):
        ctx = self.context()
        vip_uuid = 'fake-listener-id'
        cert, data = self._create_certificate()
        binding = self._build_binding(cert['id'], vip_uuid)
        self.plugin.create_a10_certificate_binding(ctx, binding)

        actual = ctx.session.query(models.CertificateListenerBinding).filter_by(
            listener_id=vip_uuid, certificate_id=cert['id']).first()

        self.assertEqual(cert['id'], actual.certificate_id)
        self.assertEqual(vip_uuid, actual.listener_id)

    def test_delete_certificate_binding(self):
        ctx = self.context()
        vip_uuid = 'fake-listener-id'
        cert, data = self._create_certificate()
        binding = self._build_binding(cert['id'], vip_uuid)
        self.plugin.create_a10_certificate_binding(ctx, binding)
        ctx.session.commit()
        record = ctx.session.query(models.CertificateListenerBinding) \
            .filter_by(listener_id=vip_uuid, certificate_id=cert['id']).first()

        self.plugin.delete_a10_certificate_binding(ctx, record.id)
        actual = ctx.session.query(models.CertificateListenerBinding).filter_by(
            listener_id=vip_uuid, certificate_id=cert['id']).first()
        self.assertTrue(actual is None)


# TODO(mdurrant) - Move this in to tests or tests/unit
class DummyCorePlugin(object):

    """Dummy Neutron Core plugin for unit testing"""
    pass


# TODO(mdurrant) - Move this in to tests or tests/unit
class DummyServicePlugin(object):

    """Dummy Neutron Service plugin for unit testing"""

    def driver_loaded(self, driver):
        pass

    def get_plugin_type(self):
        return constants.DUMMY

    def get_plugin_description(self):
        return "Dummy service plugin"


# TODO(mdurrant) - Move this in to tests or tests/unit
class DummyServiceDriver(object):

    """Dummy Neutron Service driver for unit testing"""
    @staticmethod
    def get_service_type():
        return constants.DUMMY

    def __init__(self, plugin):
        pass
