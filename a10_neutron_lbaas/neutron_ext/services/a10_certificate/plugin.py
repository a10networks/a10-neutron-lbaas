# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
from oslo_log.helpers import logging as logging

from neutron_lbaas.services.loadbalancer import plugin

from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import certificate_db as certificate_db
from a10_openstack_lib.resources import a10_certificate


LOG = logging.getLogger(__name__)


class A10CertificatePlugin(certificate_db.A10CertificateDbMixin):
    """Implementation of the Neutron SSL Certificate Plugin."""
    supported_extension_aliases = [constants.A10_CERTIFICATE_EXT]

    def __init__(self):
        super(A10CertificatePlugin, self).__init__()
        self.lbplugin = plugin.LoadBalancerPlugin()

    def get_certificates(self, context, filters=None, fields=None):
        LOG.debug("A10CertificatePlugin.get_certificates(): filters=%s, fields=%s", filters, fields)
        return super(A10CertificatePlugin, self).get_certificates(context, filters, fields)

    def create_certificate(self, context, certificate):
        LOG.debug("A10CertificatePlugin.create(): context=%s, id=%s", context, id)
        return super(A10CertificatePlugin, self).create_certificate(context, certificate)

    def get_certificate(self, context, id, fields=None):
        return super(A10CertificatePlugin, self).get_certificate(context, id)

    def update_certificate(self, context, certificate_id, certificate):
        LOG.debug("A10CertificatePlugin.update_certificate(): context=%s, cert=%s", context,
                  certificate)
        return super(A10CertificatePlugin, self).update_certificate(context, certificate_id,
                                                                 certificate)

    def delete_certificate(self, context, id):
        LOG.debug("A10CertificatePlugin.delete(): context=%s, id=%s", context, id)
        return super(A10CertificatePlugin, self).delete_certificate(context, id)

    def get_certificate_bindings(self, context, filters=None, fields=None):
        LOG.debug("A10CertificatePlugin.get_certificate_bindings(): filters=%s, fields=%s",
                  filters, fields)
        return super(A10CertificatePlugin, self).get_certificate_bindings(context, filters, fields)

    def create_certificate_binding(self, context, certificate_binding):
        LOG.debug("A10CertificatePlugin.create_certificate_binding(): binding=%s", certificate_binding)
        binding = certificate_binding["certificate_binding"]
        result = super(A10CertificatePlugin, self).create_certificate_binding(context,
                                                                           certificate_binding)

        vip_id = binding["vip_id"]
        vip = {"vip": self.lbplugin.get_vip(context, vip_id)}
        LOG.debug("A10CertificatePlugin.create_certificate_binding(): vip=%s", vip)
        self.lbplugin.update_vip(context, vip_id, vip)
        return result

    def get_certificate_binding(self, context, id, fields=None):
        return super(A10CertificatePlugin, self).get_certificate_binding(context, id)

    def delete_certificate_binding(self, context, id):
        return super(A10CertificatePlugin, self).delete_certificate_binding(context, id)

    def create_certificate_listener_binding(self, context, certificate_binding):
        binding = certificate_binding["certificate_binding"]
        result = super(A10CertificatePlugin, self).create_certificatE_listener_binding(context,
                                                                                    binding)
        listener_id = binding["listener_id"]
        listener = {"listener": self.lbplugin.get_listener(context, listener_id)}
        self.lbplugin.update_listener(context, listener_id, listener)
        return result

    def get_certificate_listener_binding(self, context, id):
        return super(A10CertificatePlugin, self).get_certificate_listener_binding(context, id)

    def get_certificate_listener_bindings(self, context, filters=None, fields=None):
        return super(A10CertificatePlugin,
                     self).get_certificate_listener_bindings(context, filters, fields)

    def delete_certificate_listener_binding(self, context, id):
        return super(A10CertificatePlugin, self).delete_certificate_listener_binding(context, id)

    def get_a10_certificates(self, context, filters=None, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificates(context, filters, fields)

    def create_a10_certificate(self, context, a10_certificate):
        return super(A10CertificatePlugin, self).create_a10_certificate(context, a10_certificate)

    def get_a10_certificate(self, context, id, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificate(context, id, fields)

    def update_a10_certificate(self, context, a10_certificate):
        return super(A10CertificatePlugin, self).update_a10_certificate(context, a10_certificate)

    def delete_a10_certificate(self, context, id):
        return super(A10CertificatePlugin, self).delete_a10_certificate(context, id)

    def get_a10_certificate_listener_bindings(self, context, filters=None, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificate_bindings(context, filters,
                                                                              fields)

    def create_a10_certificate_listener_binding(self, context, a10_certificate_binding):
        binding = a10_certificate_binding[constants.A10_CERTIFICATE_BINDING]
        result = super(A10CertificatePlugin,
                       self).create_a10_certificate_listener_binding(context,
                                                                     binding)
        listener_id = binding["listener_id"]
        listener = {"listener": self.lbplugin.get_listener(context, listener_id)}
        self.lbplugin.update_listener(context, listener_id, listener)
        return result

    def get_a10_certificate_listener_binding(self, context, id):
        return super(A10CertificatePlugin, self).get_a10_certificate_binding(context, id)

    def delete_a10_certificate_listener_binding(self, context, id):
        return super(A10CertificatePlugin, self).delete_a10_certificate_binding(context, id)
