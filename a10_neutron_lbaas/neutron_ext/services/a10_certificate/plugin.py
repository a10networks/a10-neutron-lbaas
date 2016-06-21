# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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
#    under the License.from oslo_log.helpers import logging as logging
import logging

from neutron_lbaas.services.loadbalancer import plugin

from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import certificate_db as certificate_db


LOG = logging.getLogger(__name__)


class A10CertificatePlugin(certificate_db.A10CertificateDbMixin):
    """Implementation of the Neutron SSL Certificate Plugin."""
    supported_extension_aliases = [constants.A10_CERTIFICATE_EXT]

    def __init__(self):
        super(A10CertificatePlugin, self).__init__()
        self.lbplugin = plugin.LoadBalancerPlugin()

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
