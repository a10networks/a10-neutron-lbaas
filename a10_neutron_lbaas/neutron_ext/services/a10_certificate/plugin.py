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

from a10_neutron_lbaas import constants as certificate_constants
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import certificate_db as certificate_db


LOG = logging.getLogger(__name__)


class A10CertificatePlugin(certificate_db.A10CertificateDbMixin):

    """Implementation of the Neutron SSL Certificate Plugin."""
    supported_extension_aliases = [constants.A10_CERTIFICATE_EXT]

    def __init__(self):
        super(A10CertificatePlugin, self).__init__()
        self.lbplugin = plugin.LoadBalancerPluginv2()

    def get_a10_certificates(self, context, filters=None, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificates(context, filters, fields)

    def create_a10_certificate(self, context, a10_certificate):
        return super(A10CertificatePlugin, self).create_a10_certificate(context, a10_certificate)

    def get_a10_certificate(self, context, id, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificate(context, id, fields)

    def update_a10_certificate(self, context, id, a10_certificate):
        return super(A10CertificatePlugin, self).update_a10_certificate(context, id,
                                                                        a10_certificate)

    def delete_a10_certificate(self, context, id):
        return super(A10CertificatePlugin, self).delete_a10_certificate(context, id)

    def get_a10_certificate_bindings(self, context, filters=None, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificate_bindings(context, filters,
                                                                              fields)

    def _set_a10_certificate_binding_status(self, context, id, status):
        update_binding = {
            "id": id,
            "status": status
        }
        update_a10_certificate_binding = {constants.A10_CERTIFICATE_BINDING: update_binding}

        result = super(A10CertificatePlugin,
                       self).update_a10_certificate_binding(context,
                                                            update_a10_certificate_binding)

        return result

    def _update_listener(self, context, listener_id):
        # Create an empty listener structure - we just want to trigger the update logic
        fake_listener = {"listener": {}}
        # Below will raise exception if listener doesn't exist
        self.lbplugin.update_listener(context, listener_id, fake_listener)

    def create_a10_certificate_binding(self, context, a10_certificate_binding):
        binding = a10_certificate_binding[constants.A10_CERTIFICATE_BINDING]
        created_binding = super(A10CertificatePlugin,
                                self).create_a10_certificate_binding(context,
                                                                     a10_certificate_binding)

        # All of the real work happens in the listener handler.
        self._update_listener(context, binding["listener_id"])

        result = self._set_a10_certificate_binding_status(context, created_binding["id"],
                                                          certificate_constants.STATUS_CREATED)
        return result

    def get_a10_certificate_binding(self, context, id, fields=None):
        return super(A10CertificatePlugin, self).get_a10_certificate_binding(context, id, fields)

    def delete_a10_certificate_binding(self, context, id):
        binding = self._set_a10_certificate_binding_status(context, id,
                                                           certificate_constants.STATUS_DELETING)
        # All of the real work happens in the listener handler.
        # Try to update the listener - it could be gone by now.
        try:
            self._update_listener(context, binding["listener_id"])
        except Exception as ex:
            LOG.exception(ex)
            pass

        return super(A10CertificatePlugin, self).delete_a10_certificate_binding(context, id)
