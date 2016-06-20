# Copyright (C) 2015, A10 Networks Inc. All rights reserved.

from a10_openstack.neutron_ext.common import constants
from a10_openstack.neutron_ext.extensions import a10Certificate

import gettext
_ = gettext.NullTranslations().ugettext

from neutron.common import exceptions as nexception
from neutron.db import common_db_mixin as common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from neutron_lbaas.db.loadbalancer import models as lbmodels
from neutron_lbaas.db.loadbalancer import loadbalancer_db as lbdb
from oslo_log.helpers import logging as logging
from oslo_utils import uuidutils
from sqlalchemy import orm
import sqlalchemy as sa


LOG = logging.getLogger(__name__)


# Certificate exceptions
class CertificateNotFoundError(nexception.NotFound):
    def __init__(self, certificate_id):
        self.msg = _("Certificate {} could not be found.")
        super(CertificateNotFoundError, self).__init__()


class CertificateInUseError(nexception.InUse):
    def __init__(self, certificate_id):
        self.message = _("Certificate is in use and cannot be deleted.")
        self.msg = self.message
        super(CertificateInUseError, self).__init__()


class CertificateVipBindingInUseError(nexception.InUse):
    message = _("Certificate %(certificate_id)s is still bound to %(certificatevipbinding.id)")


class CertificateVipBindingExistsError(nexception.Conflict):
    message = _("Certificate association for Certificate ID: %(certificate_id)s VIP"
                " ID: %(vip_id)s exists.")


class CertificateVipBindingNotFoundByIdError(nexception.NotFound):
    message = _("Certificate associaton for %(id)s could not be found.")


class CertificateVipBindingsNotFoundByCertificateIdError(nexception.NotFound):
    message = _("Certificate associations for %(certificate_id)s could not be found")


class CertificateVipBindingsNotFoundByVipIdError(nexception.NotFound):
    message = _("Certificate associations for %(vip_id)s could not be found")


class CertificateVipBindingsNotFoundByCertificateVipComboError(nexception.NotFound):
    message = _("Certificate associatons for Certificate ID %(certificate_id)s / "
                "VIP ID %(vip_id)s could not be found")


class CertificateListenerBindingInUseError(nexception.InUse):
    message = _("Certificate %(certificate_id)s is still bound to %(certificatelistenerbinding.id)")


class CertificateListenerBindingExistsError(nexception.Conflict):
    message = _("Certificate association for Certificate ID: %(certificate_id)s Listener"
                " ID: %(listener_id)s exists.")


class CertificateListenerBindingNotFoundByIdError(nexception.NotFound):
    message = _("Certificate associaton for %(id)s could not be found.")


class CertificateListenerBindingsNotFoundByCertificateIdError(nexception.NotFound):
    message = _("Certificate associations for %(certificate_id)s could not be found")


class CertificateListenerBindingsNotFoundByListenerIdError(nexception.NotFound):
    message = _("Certificate associations for %(listener_id)s could not be found")


class CertificateListenerBindingsNotFoundByCertificateListenerComboError(nexception.NotFound):
    message = _("Certificate associatons for Certificate ID %(certificate_id)s / "
                "Listener ID %(listener_id)s could not be found")


class Certificate(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    __tablename__ = "certificates"
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text(1024), nullable=True)
    cert_data = sa.Column(sa.Text(8000), nullable=False)
    key_data = sa.Column(sa.Text(8000), nullable=False)
    intermediate_data = sa.Column(sa.Text(8000), nullable=True)
    password = sa.Column(sa.String(1024), nullable=True)


class CertificateVipBinding(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    __tablename__ = "certificatevipbindings"
    certificate_id = sa.Column(sa.String(36), sa.ForeignKey("certificates.id"),
                               nullable=False)
    certificate = orm.relationship(Certificate, uselist=False)
    vip = orm.relationship(lbdb.Vip, uselist=False)
    vip_id = sa.Column(sa.String(36), sa.ForeignKey("vips.id"), nullable=False)


class CertificateListenerBinding(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    __tablename__ = "a10_certificatelistenerbindings"
    certificate_id = sa.Column(sa.String(36), sa.ForeignKey("certificates.id"),
                               nullable=False)
    certificate = orm.relationship(Certificate, uselist=False)
    listener_id = sa.Column(sa.String(36), sa.ForeignKey("lbaas_listeners.id"))
    listener = orm.relationship(lbmodels.Listener, uselist=False)


class A10CertificateDbMixin(common_db_mixin.CommonDbMixin, a10Certificate.A10CertificatePluginBase):
    """Class to support SSL certificates and their association with VIPs."""
    def __init__(self):
        # manager = None is used in unit tests where CertificateManager is loaded as a plugin.
        pass

    def get_plugin_name(self):
        return constants.A10_CERTIFICATE

    def get_plugin_type(self):
        return constants.A10_CERTIFICATE

    def get_plugin_description(self):
        return "Neutron Certificates and VIPs plugin"

    def _get_certificate(self, context, certificate_id):
        try:
            return self._get_by_id(context, Certificate, certificate_id)
        except Exception:
            raise CertificateNotFoundError(certificate_id=certificate_id)

    def _make_certificate_dict(self, certificate_db, fields=None):
        res = {'id': certificate_db['id'],
               'name': certificate_db['name'],
               'tenant_id': certificate_db['tenant_id'],
               'description': certificate_db['description'],
               'cert_data': certificate_db['cert_data'],
               'key_data': certificate_db['key_data'],
               'intermediate_data': certificate_db['intermediate_data'],
               'password': certificate_db['password']}
        return self._fields(res, fields)

    def _ensure_certificate_not_in_use(self, context, certificate_id):
        with context.session.begin(subtransactions=True):
            vips = (context.session.query(CertificateVipBinding)
                    .filter_by(certificate_id=certificate_id)
                    .join(lbdb.Vip, lbdb.Vip.id == CertificateVipBinding.vip_id)
                    ).all()
            LOG.debug("CertificateDbMixin:_ensure_certificate_not_in_use(): id={0}, len={1}".format(
                certificate_id, len(vips)))

        if vips is not None and len(vips) > 0:
            raise CertificateInUseError(certificate_id)

    def create_certificate(self, context, certificate):
        cert = certificate['certificate']
        with context.session.begin(subtransactions=True):
            cert_record = Certificate(id=uuidutils.generate_uuid(),
                                      name=cert['name'],
                                      description=cert['description'],
                                      cert_data=cert['cert_data'],
                                      key_data=cert['key_data'],
                                      intermediate_data=cert['intermediate_data'],
                                      password=cert['password'],
                                      tenant_id=context.tenant_id)
            context.session.add(cert_record)

        return self._make_certificate_dict(cert_record)

    def update_certificate(self, context, certificate_id, certificate):
        data = certificate['certificate']
        with context.session.begin(subtransactions=True):
            certificate_db = self._get_certificate(context, certificate_id)
            certificate_db.update(data)

        return self._make_certificate_dict(certificate_db)

    def delete_certificate(self, context, certificate_id):
        with context.session.begin(subtransactions=True):
            self._ensure_certificate_not_in_use(context, certificate_id)
            LOG.debug("CertificateDbMixin:delete_certificate(): certificate_id={0}".format(
                certificate_id))
            cert = self._get_certificate(context, certificate_id)
            context.session.delete(cert)

    def get_certificate(self, context, certificate_id, fields=None):
        cert = self._get_certificate(context, certificate_id)
        return self._make_certificate_dict(cert, fields)

    def get_certificates_for_vip(self, context, vip_id):
        with context.session.begin(subtransactions=True):
            certs = (context.session.query(CertificateVipBinding)
                     .filter_by(vip_id=vip_id)
                     .join(Certificate, Certificate.id == CertificateVipBinding.certificate_id)
                     ).all()

        return certs

    def get_vips_for_certificate(self, context, certificate_id):
        with context.session.begin(subtransactions=True):
            vips = (context.session.query(CertificateVipBinding)
                    .filter_by(id=certificate_id)
                    .join(lbdb.Vip, lbdb.Vip.id == CertificateVipBinding.vip_id)
                    ).all()

        return vips

    def get_certificates(self, context, filters=None, fields=None,
                         sorts=None, limit=None, marker=None,
                         page_reverse=False):
        LOG.debug("NDB: CertificateDbMixin:get_certificates() tenant_id=%s" % context.tenant_id)
        return self._get_collection(context, Certificate,
                                    self._make_certificate_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)

    def _get_binding(self, context, binding_id):
        try:
            return self._get_by_id(context, CertificateVipBinding, binding_id)
        except Exception:
            raise CertificateVipBindingNotFoundByIdError(id=binding_id)

    def _make_binding_dict(self, binding, fields=None):
        res = {'id': binding['id'],
               'tenant_id': binding['tenant_id'],
               'certificate_id': binding['certificate_id'],
               'vip_id': binding['vip_id'],
               'certificate_name': binding.certificate['name'],
               'vip_name': binding.vip['name']}
        return self._fields(res, fields)

    def _make_listener_binding_dict(self, binding, fields=None):
        res = {'id': binding['id'],
               'tenant_id': binding['tenant_id'],
               'certificate_id': binding['certificate_id'],
               'listener_id': binding['listener_id'],
               'certificate_name': binding.certificate['name'],
               'listener_name': binding.listener['name']}
        return self._fields(res, fields)


    def get_certificate_binding(self, context, id, fields=None):
        binding = self._get_binding(context, id)
        LOG.debug("CertificateDbMixin:get_certificate_binding(): %s" % binding)
        return self._make_binding_dict(binding, fields)

    def create_certificate_binding(self, context, certificate_binding):
        binding = certificate_binding['certificate_binding']
        certificate_id = binding['certificate_id']
        vip_id = binding['vip_id']
        with context.session.begin(subtransactions=True):
            existing = (context.session.query(CertificateVipBinding)
                        .filter_by(certificate_id=certificate_id, vip_id=vip_id)
                        .first())
            if existing is not None:
                raise CertificateVipBindingExistsError(certificate_id=certificate_id,
                                                       vip_id=vip_id)
            binding_record = CertificateVipBinding(id=uuidutils.generate_uuid(),
                                                   certificate_id=certificate_id,
                                                   vip_id=vip_id,
                                                   tenant_id=context.tenant_id)
            context.session.add(binding_record)

        return self._make_binding_dict(binding_record)

    def delete_certificate_binding(self, context, id):
        with context.session.begin(subtransactions=True):
            binding = self._get_binding(context, id)
            if binding is None:
                raise CertificateVipBindingNotFoundByIdError(id=id)
            context.session.delete(binding)

    def get_certificate_bindings(self, context, filters=None, fields=None,
                                 sorts=None, limit=None, marker=None,
                                 page_reverse=False):
        bindings = self._get_collection(context, CertificateVipBinding,
                                        self._make_binding_dict, filters=filters,
                                        fields=fields, sorts=sorts, limit=limit,
                                        marker_obj=marker, page_reverse=page_reverse)
        return bindings

    def create_a10_certificate(self, context, a10_certificate):
        # TODO replace string with ref to res
        cert = a10_certificate['a10_certificate']
        with context.session.begin(subtransactions=True):
            cert_record = Certificate(id=uuidutils.generate_uuid(),
                                      name=cert['name'],
                                      description=cert['description'],
                                      cert_data=cert['cert_data'],
                                      key_data=cert['key_data'],
                                      intermediate_data=cert['intermediate_data'],
                                      password=cert['password'],
                                      tenant_id=context.tenant_id)
            context.session.add(cert_record)

        return self._make_certificate_dict(cert_record)

    def update_a10_certificate(self, context, certificate_id, certificate):
        data = certificate['certificate']
        with context.session.begin(subtransactions=True):
            certificate_db = self._get_certificate(context, certificate_id)
            certificate_db.update(data)

        return self._make_certificate_dict(certificate_db)

    def delete_a10_certificate(self, context, certificate_id):
        with context.session.begin(subtransactions=True):
            self._ensure_certificate_not_in_use(context, certificate_id)
            LOG.debug("CertificateDbMixin:delete_certificate(): certificate_id={0}".format(
                certificate_id))
            cert = self._get_certificate(context, certificate_id)
            context.session.delete(cert)

    def _get_listener_binding(self, context, binding_id):
        import pdb; pdb.set_trace()
        try:
            return self._get_by_id(context, CertificateListenerBinding, binding_id)
        except Exception:
            raise CertificateListenerBindingNotFoundByIdError(id=binding_id)

    def get_a10_certificate(self, context, certificate_id, fields=None):
        cert = self._get_certificate(context, certificate_id)
        return self._make_certificate_dict(cert, fields)

    def get_a10_certificates(self, context, filters=None, fields=None,
                         sorts=None, limit=None, marker=None,
                         page_reverse=False):
        LOG.debug("NDB: CertificateDbMixin:get_certificates() tenant_id=%s" % context.tenant_id)
        return self._get_collection(context, Certificate,
                                    self._make_certificate_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)

    def get_a10_certificate_binding(self, context, id, fields=None):
        binding = self._get_listener_binding(context, id)
        LOG.debug("CertificateDbMixin:get_certificate_binding(): %s" % binding)
        return self._make_listener_binding_dict(binding, fields)

    def create_a10_certificate_binding(self, context, a10_certificate_binding):
        binding = a10_certificate_binding['a10_certificate_binding']
        certificate_id = binding['certificate_id']
        listener_id = binding['listener_id']
        with context.session.begin(subtransactions=True):
            existing = (context.session.query(CertificateListenerBinding)
                        .filter_by(certificate_id=certificate_id, listener_id=listener_id)
                        .first())
            if existing is not None:
                raise CertificateListenerBindingExistsError(certificate_id=certificate_id,
                                                       listener_id=listener_id)
            binding_record = CertificateListenerBinding(id=uuidutils.generate_uuid(),
                                                   certificate_id=certificate_id,
                                                   listener_id=listener_id,
                                                   tenant_id=context.tenant_id)
            context.session.add(binding_record)

        return self._make_listener_binding_dict(binding_record)

    def delete_a10_certificate_binding(self, context, id):
        import pdb; pdb.set_trace()
        with context.session.begin(subtransactions=True):
            binding = self._get_listener_binding(context, id)
            if binding is None:
                raise CertificateListenerBindingNotFoundByIdError(id=id)
            context.session.delete(binding)

    def get_a10_certificate_bindings(self, context, filters=None, fields=None,
                                 sorts=None, limit=None, marker=None,
                                 page_reverse=False):
        bindings = self._get_collection(context, CertificateListenerBinding,
                                        self._make_listener_binding_dict, filters=filters,
                                        fields=fields, sorts=sorts, limit=limit,
                                        marker_obj=marker, page_reverse=page_reverse)
        return bindings

    def get_certificates_for_listener(self, context, listener_id):
        rv = []
        with context.session.begin(subtransactions=True):
            rv = (context.session.query(CertificateListenerBinding)
                     .filter_by(listener_id=listener_id)
                     .join(Certificate,
                           Certificate.id == CertificateListenerBinding.certificate_id)
                     ).all()

        return rv

    def get_listeners_for_certificate(self, context, certificate_id):
        rv = []
        with context.session.begin(subtransactions=True):
            rv = (context.session.query(CertificateListenerBinding)
                    .filter_by(id=certificate_id)
                    .join(lbdb.Listener,
                          lbdb.Listener.id == CertificateListenerBinding.listener_id)
                    ).all()

        return rv
