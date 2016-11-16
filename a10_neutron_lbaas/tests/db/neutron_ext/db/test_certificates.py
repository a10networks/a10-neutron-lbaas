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
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import certificate_db as certs_db
from a10_neutron_lbaas.neutron_ext.extensions import a10Certificate as certificate
from a10_neutron_lbaas.tests.db import test_base as tbase

import mock
from neutron import context
from neutron.db import models_v2

from neutron.tests.unit.api.v2 import test_base as test_api_v2_extension
from neutron.tests.unit.extensions import base
from neutron.tests.unit import testlib_api
from neutron_lbaas.db.loadbalancer import loadbalancer_dbv2 as lbdb
from oslo_config import cfg
from oslo_log.helpers import logging as logging
from oslo_utils import uuidutils

import sqlalchemy

import os
import os.path


LOG = logging.getLogger(__name__)

_tenant_id = uuidutils.generate_uuid()
_get_path = test_api_v2_extension._get_path


class CertificateExtensionTestCase(base.ExtensionTestCase):

    """Tests a10_openstack.neutron_ext.extensions.Certificates"""

    def setUp(self):
        super(CertificateExtensionTestCase, self).setUp()
        self.plugin = mock.MagicMock()
        self.plugin.return_value = mock.MagicMock()
        # self.fmt = "/{0}/{1}"
        self._setUpExtension(
            'a10_neutron_lbaas.neutron_ext.db.certificate_db.A10CertificateDbMixin',
            constants.A10_CERTIFICATE, certificate.RESOURCE_ATTRIBUTE_MAP,
            certificate.A10Certificate, '', supported_extension_aliases='certificate'
        )

    def _build_test_binding_collection(self):
        result = {"certificate_bindings": []}
        result["certificate_bindings"].append(self._build_test_binding(
            uuidutils.generate_uuid(),
            uuidutils.generate_uuid(),
            _tenant_id))
        result["certificate_bindings"].append(self._build_test_binding(
            uuidutils.generate_uuid(),
            uuidutils.generate_uuid(),
            _tenant_id))
        result["certificate_bindings"].append(self._build_test_binding(
            uuidutils.generate_uuid(),
            uuidutils.generate_uuid(),
            _tenant_id))
        return result

    def _build_test_certificate_collection(self):
        result = {"certificates": []}

        result["certificates"].append(self._build_test_certificate())
        result["certificates"].append(self._build_test_certificate(
            name="Magic Certificate 2"))
        return result

    def _build_test_binding(self, certificate_id, vip_id, tenant_id=_tenant_id):
        result = {'certificate_id': certificate_id,
                  'vip_id': vip_id}
        if tenant_id is not None:
            result['tenant_id'] = tenant_id
        return result

    def _build_test_certificate(self, name="Magic Certificate",
                                description="Certificate Description",
                                cert_data="Super secret certificate data",
                                key_data='Key data',
                                intermediate_data='Intermediate data',
                                tenant_id=_tenant_id,
                                password="SecretPassword"):
        result = {'name': name,
                  'description': description,
                  'cert_data': cert_data,
                  'key_data': key_data,
                  'intermediate_data': intermediate_data,
                  'password': password}
        if tenant_id is not None:
            result['tenant_id'] = tenant_id
        return result

    def test_create_certificate(self):
        expected = {'certificate': self._build_test_certificate(_tenant_id)}

        instance = self.plugin.return_value
        instance.create_certificate.return_value = expected["certificate"]

        self.api.post(_get_path("certificates", fmt=self.fmt), self.serialize(expected),
                      content_type='application/%s' % self.fmt)
        instance.create_certificate.assert_called_with(mock.ANY, certificate=expected)

    def test_delete_certificate(self):
        certificate_id = uuidutils.generate_uuid()
        instance = self.plugin.return_value
        self.api.delete(_get_path("certificates", id=certificate_id, fmt=self.fmt),
                        content_type="application/%s" % self.fmt)

        instance.delete_certificate.assert_called_with(mock.ANY, certificate_id)

    def test_update_certificate(self):
        certificate_id = uuidutils.generate_uuid()
        expected = {'certificate': self._build_test_certificate(tenant_id=None)}
        instance = self.plugin.return_value
        instance.update_certificate.return_value = expected
        self.api.put(_get_path("certificates", id=certificate_id, fmt=self.fmt),
                     self.serialize(expected),
                     content_type="application/%s" % self.fmt)

        instance.update_certificate.assert_called_with(mock.ANY,
                                                       certificate_id,
                                                       certificate=expected)

    def test_get_certificate(self):
        certificate_id = uuidutils.generate_uuid()
        expected = {'a10_certificate': self._build_test_certificate()}
        instance = self.plugin.return_value
        instance.get_certificate.return_value = expected['a10_certificate']
        response = self.api.get(_get_path("a10_certificates", id=certificate_id, fmt=self.fmt))
        instance.get_certificate.assert_called_with(mock.ANY, certificate_id, fields=mock.ANY)
        actual = self.deserialize(response)
        self.assertEqual(1, len(actual))
        self.assertEqual(expected, actual)
        self.assertEqual(expected['a10_certificate']['name'], actual['a10_certificate']['name'])

    def test_get_certificates(self):
        expected = self._build_test_certificate_collection()
        instance = self.plugin.return_value
        instance.get_certificates.return_value = expected['certificates']
        url = _get_path("certificates", fmt=self.fmt)
        response = self.api.get(url)

        instance.get_a10_certificates.assert_called_with(mock.ANY,
                                                         fields=mock.ANY,
                                                         filters=mock.ANY)
        actual = self.deserialize(response)
        self.assertEqual(expected['certificates'], actual['certificates'])

    def test_get_certificate_binding(self):
        binding_id = uuidutils.generate_uuid()
        certificate_id = uuidutils.generate_uuid()
        vip_id = uuidutils.generate_uuid()
        expected = {'certificate_binding': self._build_test_binding(certificate_id, vip_id)}
        instance = self.plugin.return_value
        instance.get_certificate_binding.return_value = expected["certificate_binding"]
        url = _get_path("certificate-bindings", id=binding_id, fmt=self.fmt)
        response = self.api.get(url)
        instance.get_certificate_binding.assert_called_with(mock.ANY, binding_id, fields=mock.ANY)
        actual = self.deserialize(response)
        self.assertEqual(expected, actual)
        self.assertEqual("200 OK", response._status)

    def test_get_certificate_bindings(self):
        expected = self._build_test_binding_collection()

        instance = self.plugin.return_value
        instance.get_certificate_bindings.return_value = expected['certificate_bindings']
        url = _get_path("certificate-bindings", fmt=self.fmt)
        result = self.api.get(url)
        actual = self.deserialize(result)

        instance.get_certificate_bindings.assert_called_with(mock.ANY,
                                                             fields=mock.ANY,
                                                             filters=mock.ANY)
        self.assertEqual(expected, actual)

    def test_create_certificate_binding(self):
        certificate_id = uuidutils.generate_uuid()
        vip_id = uuidutils.generate_uuid()
        expected = {'certificate_binding': self._build_test_binding(certificate_id, vip_id)}
        instance = self.plugin.return_value
        instance.create_certificate_binding.return_value = expected  # ["certificate_binding"]
        url = _get_path("certificate-bindings", fmt=self.fmt)
        self.api.post(url, self.serialize(expected),
                      content_type='application/%s' % self.fmt)
        instance.create_certificate_binding.assert_called_with(mock.ANY,
                                                               certificate_binding=expected)

    def test_delete_certificate_binding(self):
        binding_id = uuidutils.generate_uuid()
        instance = self.plugin.return_value
        url = _get_path("certificate-bindings", id=binding_id, fmt=self.fmt)
        self.api.delete(url, content_type="application/%s" % self.fmt)
        instance.delete_certificate_binding.assert_called_with(mock.ANY, binding_id)


class CertificateDbMixInTestCase(testlib_api.OpportunisticDBTestMixin,
                                 tbase.UnitTestBase):

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
        self.engine = sqlalchemy.create_engine("sqlite://")
        super(CertificateDbMixInTestCase, self).setUp()

        # Following line no qa'd
        args = ['--config-file', self._test_conf_path]  # noqa

        # self.config_parse(args=args)
        # cfg.CONF.set_override('policy_file', self._neutron_policy)
        cfg.CONF.set_override(
            'core_plugin',
            # TODO(mdurrant) - Move this in to tests or tests/unit
            'a10_neutron_lbaas.tests.unit.neutron_ext.db.test_certificates.DummyCorePlugin'
        )
        cfg.CONF.set_override(
            'service_plugins',
            # TODO(mdurrant) - Move this in to tests or tests/unit
            ['a10_neutron_lbaas.tests.unit.db.test_certificates.DummyServicePlugin',
             'a10_neutron_lbaas.neutron_ext.services.a10_certificate.plugin.A10CertificatePlugin']
        )

        self.plugin = certs_db.A10CertificateDbMixin()  # manager.NeutronManager().get_instance()

        # self.plugin.context.session.get_engine(sqlite_fk=True)
        # self.session.get_engine(sqlite_fk=True)

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

    def _build_binding(self, certificate_id=None, vip_id=None, tenant_id=None):
        return {'certificate_binding': {'certificate_id': certificate_id,
                                        'vip_id': vip_id,
                                        'tenant_id': tenant_id}}

    def _create_certificate(self, tenant_id='tenant1', ctx=None, description=None):
        if ctx is None:
            ctx = context.get_admin_context()
        ctx.tenant_id = tenant_id
        certificate = self._build_certificate()
        return self.plugin.create_a10_certificate(ctx, certificate), certificate

    def _create_binding(self, ctx=None, certificate_id=None, vip_id=None, tenant_id=_tenant_id):
        if ctx is None:
            ctx = self.admin_ctx
        ctx.tenant_id = tenant_id
        binding = self._build_binding(ctx, certificate_id, vip_id, tenant_id)

        return self.plugin.create_a10_certificate_listener_binding(ctx, binding), binding

    def _build_vip_dependencies(self, ctx, tenant_id):
        """Builds Network => Port => Vip to satisfy foreign key constraints"""
        lb = lbdb.LoadBalancer()
        if ctx is None:
            ctx = context.get_admin_context()
        with ctx.session.begin():
            network = models_v2.Network(id=uuidutils.generate_uuid(),
                                        name='Test Network',
                                        status='Unavailable',
                                        admin_state_up=False)

            ctx.session.add(network)
            network = ctx.session.query(models_v2.Network).filter_by(name='Test Network').first()
            port = models_v2.Port(id=uuidutils.generate_uuid(),
                                  name='Test Port', tenant_id=tenant_id,
                                  network_id=network['id'],
                                  mac_address='13:37:c0:ff:fe:13', admin_state_up=False,
                                  device_owner='Test Owner', device_id='Test Device ID',
                                  status='INACTIVE')

            ctx.session.add(port)
            port = ctx.session.query(models_v2.Port).filter_by(name='Test Port').first()
            # TODO(mdurrant) What does protocol_port do?
            lb = lbdb.LoadBalancer(id=uuidutils.generate_uuid(),
                                   name='Test Vip', description='Test Vip Description',
                                   port_id=port['id'], protocol_port=0, protocol='HTTPS',
                                   pool_id=uuidutils.generate_uuid(), tenant_id=tenant_id,
                                   status='INACTIVE', status_description='INACTIVE',
                                   admin_state_up=False, connection_limit=42)

            ctx.session.add(listener)
            listener = ctx.session.query(lbdb.LoadBalancer).filter_by(name='Test Listener').first()
        return lb

    def test_create_certificate(self, tenant_id="tenant1"):
        ctx = context.get_admin_context()
        record, request = self._create_certificate(tenant_id)
        res = ctx.session.query(certs_db.Certificate).all()
        self.assertEqual(1, len(res))
        actual = res[0]
        self.assertFalse(actual is None)
        self.assertEqual(self._test_name, actual['name'])
        self.assertEqual(self._test_description, actual['description'])
        self.assertEqual(self._test_cert_data, actual['cert_data'])
        self.assertEqual(self._test_key_data, actual['key_data'])
        self.assertEqual(self._test_intermediate_data, actual['intermediate_data'])
        self.addCleanup(ctx.session.delete, actual)

    def test_update_certificate(self):
        ctx = context.get_admin_context()
        cert, certificate = self._create_certificate(ctx=ctx)
        certificate = {'certificate': {'name': 'THE SECOND CERTIFICATE',
                                       'description': 'THE SECOND CERT DESCRIBED',
                                       'cert_data': 'M0re s00p3r s3cr3t d@ta',
                                       'key_data': 'Key data',
                                       'intermediate_data': 'intermediate data',
                                       'password': 'password'}}
        self.plugin.update_a10_certificate(ctx, cert['id'], certificate)
        actual = (ctx.session.query(certs_db.Certificate).filter_by(id=cert['id']).one())
        self.assertEqual('THE SECOND CERTIFICATE', actual['name'])
        self.assertEqual('THE SECOND CERT DESCRIBED', actual['description'])
        self.assertEqual('M0re s00p3r s3cr3t d@ta', actual['cert_data'])

    def test_delete_certificate(self):
        ctx = context.get_admin_context()
        cert, data = self._create_certificate(ctx=ctx)
        self.plugin.delete_a10_certificate(ctx, cert['id'])
        actual = (ctx.session.query(certs_db.Certificate).filter_by(id=cert['id']).first())
        self.assertTrue(actual is None)

    def test_get_certificate(self):
        ctx = context.get_admin_context()
        cert, data = self._create_certificate()
        actual = self.plugin.get_a10_certificate(ctx, cert['id'])
        self.assertEqual(cert, actual)

    def test_get_throwsexceptionwhenitdoesntexist(self):
        ctx = context.get_admin_context()
        self.assertRaises(certs_db.CertificateNotFoundError, self.plugin.get_a10_certificate,
                          (self, ctx, uuidutils.generate_uuid()), None)

    def test_create_certificate_binding(self):
        ctx = context.get_admin_context()
        vip = self._build_vip_dependencies(ctx, _tenant_id)
        vip_uuid = vip['id']
        cert, data = self._create_certificate()
        binding = self._build_binding(cert['id'], vip_uuid)
        self.plugin.create_a10_certificate_listener_binding(ctx, binding)

        actual = ctx.session.query(certs_db.CertificateVipBinding).filter_by(
            vip_id=vip_uuid, certificate_id=cert['id']).first()

        self.assertEqual(cert['id'], actual.certificate_id)
        self.assertEqual(vip_uuid, actual.vip_id)

    def test_delete_certificate_binding(self):
        ctx = context.get_admin_context()
        vip = self._build_vip_dependencies(ctx, _tenant_id)
        vip_uuid = vip['id']

        cert, data = self._create_certificate()
        binding = self._build_binding(cert['id'], vip_uuid)
        self.plugin.create_a10_certificate_listener_binding(ctx, binding)
        record = ctx.session.query(certs_db.CertificateVipBinding) \
            .filter_by(vip_id=vip_uuid, certificate_id=cert['id']).first()
        self.plugin.delete_a10_certificate_listener_binding(ctx, record['id'])
        actual = ctx.session.query(certs_db.CertificateVipBinding).filter_by(
            vip_id=vip_uuid, certificate_id=cert['id']).first()
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
