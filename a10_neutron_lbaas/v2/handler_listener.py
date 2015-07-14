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

import a10_neutron_lbaas.a10_openstack_map as a10_osmap

from neutron_lbaas.services.loadbalancer import constants as lb_const

import acos_client.errors as acos_errors
import handler_base_v2
import handler_persist
import v2_context as a10

import a10_neutron_lbaas.v2.wrapper_certmgr as certwrapper

import pdb

LOG = logging.getLogger(__name__)


class ListenerHandler(handler_base_v2.HandlerBaseV2):
    def __init__(self, a10_driver, openstack_manager, neutron=None, barbican_client=None):
        super(ListenerHandler, self).__init__(a10_driver, openstack_manager, neutron)
        self.barbican_client = barbican_client

    def _set(self, set_method, c, context, listener):
        if self.barbican_client is None:
            self.barbican_client = certwrapper.CertManagerWrapper()

        status = c.client.slb.UP
        if not listener.admin_state_up:
            status = c.client.slb.DOWN

        templates = self.meta(listener, "template", {})

        # client_args = {}
        server_args = {}
        cert_data = dict()

        pdb.set_trace()

        if listener.protocol and listener.protocol == lb_const.PROTOCOL_TERMINATED_HTTPS:
            self._set_terminated_https_values(listener, c, cert_data)
            templates["client_ssl"] = {}

            template_name = str(cert_data.get('template_name', ''))
            key_passphrase = str(cert_data.get('cert_pass', ''))
            cert_filename = str(cert_data.get('cert_filename', ''))
            key_filename = str(cert_data.get('key_filename', ''))

        if 'client_ssl' in templates:
            client_args = {'client_ssl_template': templates['client_ssl']}
            try:
                c.client.slb.template.client_ssl.create(
                    template_name,
                    cert=cert_filename,
                    key=key_filename)
            except acos_errors.Exists:
                c.client.slb.template.client_ssl.update(template_name, cert=cert_filename,
                                                        key=key_filename, passphrase=key_passphrase)

        if 'server_ssl' in templates:
            server_args = {'server_ssl_template': templates['server_ssl']}
            try:
                c.client.slb.template.server_ssl.create(
                    template_name,
                    cert_filename,
                    key_filename,
                    axapi_args=server_args)
            except acos_errors.Exists:
                pass

        try:
            pool_name = self._pool_name(context, listener.default_pool)
        except Exception:
            pool_name = None
        persistence = handler_persist.PersistHandler(
            c, context, listener.default_pool)
        vport_args = {'port': self.meta(listener, 'port', {})}

        try:
            set_method(
                self.a10_driver.loadbalancer._name(listener.loadbalancer),
                self._meta_name(listener),
                protocol=a10_osmap.vip_protocols(c, listener.protocol),
                port=listener.protocol_port,
                service_group_name=pool_name,
                s_pers_name=persistence.s_persistence(),
                c_pers_name=persistence.c_persistence(),
                status=status,
                axapi_args=vport_args)
        except acos_errors.Exists:
            pass

    def _set_terminated_https_values(self, listener, c, cert_data):
        c_id = listener.default_tls_container_id if listener.default_tls_container_id else None

        container = self.barbican_client.get_certificate(c_id, check_only=True)
        if container:
            base_name = (container._cert_container.name if container._cert_container is not None
                         else "")

            cert_data["cert_content"] = container.get_certificate()
            cert_data["key_content"] = container.get_private_key()
            cert_data["cert_pass"] = container.get_private_key_passphrase()

            cert_data["template_name"] = listener.id

            cert_data["cert_filename"] = "{0}cert.pem".format(base_name)
            cert_data["key_filename"] = "{0}key.pem".format(base_name)

            if c.client.file.ssl_cert.exists(cert_data["cert_filename"]):
                c.client.file.ssl_cert.update(cert_data["cert_filename"],
                                              cert_data["cert_content"],
                                              len(cert_data["cert_content"]),
                                              action="import", certificate_type="pem")
            else:
                c.client.file.ssl_cert.create(cert_data["cert_filename"],
                                              cert_data["cert_content"],
                                              len(cert_data["cert_content"]),
                                              action="import", certificate_type="pem")

            if c.client.file.ssl_key.exists(cert_data["key_filename"]):
                c.client.file.ssl_key.update(cert_data["key_filename"],
                                             cert_data["key_content"],
                                             len(cert_data["key_content"]),
                                             action="import")
            else:
                c.client.file.ssl_key.create(cert_data["key_filename"],
                                             cert_data["key_content"],
                                             len(cert_data["key_content"]),
                                             action="import")

    def _create(self, c, context, listener):
        self._set(c.client.slb.virtual_server.vport.create,
                  c, context, listener)

    def create(self, context, listener):
        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._create(c, context, listener)

    def _update(self, c, context, listener):
        self._set(c.client.slb.virtual_server.vport.update, c, context, listener)

    def update(self, context, old_listener, listener):
        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._update(c, context, listener)

    def _delete(self, c, context, listener):
        c.client.slb.virtual_server.vport.delete(
            self.a10_driver.loadbalancer._name(listener.loadbalancer),
            self._meta_name(listener),
            protocol=a10_osmap.vip_protocols(c, listener.protocol),
            port=listener.protocol_port)

    def delete(self, context, listener):
        with a10.A10DeleteContext(self, context, listener) as c:
            self._delete(c, context, listener)

    def set_certmgr(self, certmgr):
        self.barbican_client = certmgr
