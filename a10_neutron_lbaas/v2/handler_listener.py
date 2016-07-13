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

import acos_client.errors as acos_errors

from a10_neutron_lbaas.acos import openstack_mappings
from a10_neutron_lbaas import constants
import a10_neutron_lbaas.v2.wrapper_certmgr as certwrapper
import handler_base_v2
import handler_persist
import v2_context as a10


LOG = logging.getLogger(__name__)


class ListenerHandler(handler_base_v2.HandlerBaseV2):
    def __init__(self, a10_driver, openstack_manager, neutron=None, barbican_client=None):
        super(ListenerHandler, self).__init__(a10_driver, openstack_manager, neutron)
        self.barbican_client = barbican_client

    def _set(self, set_method, c, context, listener):
        if self.barbican_client is None:
            self.barbican_client = certwrapper.CertManagerWrapper(handler=self)

        status = c.client.slb.UP
        if not listener.admin_state_up:
            status = c.client.slb.DOWN

        templates = self.meta(listener, "template", {})

        server_args = {}
        cert_data = dict()
        template_args = {}

        if listener.protocol and listener.protocol == constants.PROTOCOL_TERMINATED_HTTPS:
            if self._set_terminated_https_values(listener, c, cert_data):
                templates["client_ssl"] = {}
                template_name = str(cert_data.get('template_name', ''))
                key_passphrase = str(cert_data.get('key_pass', ''))
                cert_filename = str(cert_data.get('cert_filename', ''))
                key_filename = str(cert_data.get('key_filename', ''))
            else:
                LOG.error("Could not created terminated HTTPS endpoint.")

        if 'client_ssl' in templates:
            template_args["template_client_ssl"] = template_name
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
            template_args["template_server_ssl"] = template_name
            try:
                c.client.slb.template.server_ssl.create(
                    template_name,
                    cert_filename,
                    key_filename,
                    axapi_args=server_args)
            except acos_errors.Exists:
                c.client.slb.template.server_ssl.update(template_name,
                                                        cert_filename,
                                                        key_filename,
                                                        axapi_args=server_args)

        try:
            pool_name = self._pool_name(context, pool_id=listener.default_pool_id)
        except Exception:
            pool_name = None

        persistence = handler_persist.PersistHandler(
            c, context, listener.default_pool)

        vport_meta = self.meta(listener.loadbalancer, 'vip_port', {})

        try:
            set_method(
                self.a10_driver.loadbalancer._name(listener.loadbalancer),
                self._meta_name(listener),
                protocol=openstack_mappings.vip_protocols(c, listener.protocol),
                port=listener.protocol_port,
                service_group_name=pool_name,
                s_pers_name=persistence.s_persistence(),
                c_pers_name=persistence.c_persistence(),
                status=status,
                autosnat=c.device_cfg.get('autosnat'),
                ipinip=c.device_cfg.get('ipinip'),
                axapi_body=vport_meta,
                **template_args)
        except acos_errors.Exists:
            pass

    def _set_terminated_https_values(self, listener, c, cert_data):
        is_success = False
        c_id = listener.default_tls_container_id if listener.default_tls_container_id else None

        if c_id:
            try:
                container = self.barbican_client.get_certificate(c_id, check_only=True)
            except Exception as ex:
                container = None
                LOG.error("Exception encountered retrieving TLS Container %s" % c_id)
                LOG.exception(ex)

            if container:
                base_name = getattr(getattr(container, '_cert_container', None), 'name', '') or c_id

                cert_data["cert_content"] = container.get_certificate()
                cert_data["key_content"] = container.get_private_key()
                cert_data["key_pass"] = container.get_private_key_passphrase()

                cert_data["template_name"] = listener.id

                cert_data["cert_filename"] = "{0}cert.pem".format(base_name)
                cert_data["key_filename"] = "{0}key.pem".format(base_name)

                self._acos_create_or_update(c.client.file.ssl_cert,
                                            file=cert_data["cert_filename"],
                                            cert=cert_data["cert_content"],
                                            size=len(cert_data["cert_content"]),
                                            action="import", certificate_type="pem")

                self._acos_create_or_update(c.client.file.ssl_key,
                                            file=cert_data["key_filename"],
                                            cert=cert_data["key_content"],
                                            size=len(cert_data["key_content"]),
                                            action="import")
                is_success = True
        else:
            LOG.error("default_tls_container_id unspecified for listener. Cannot create listener.")
        return is_success

    def _acos_create_or_update(self, acos_obj, **kwargs):
        try:
            acos_obj.create(**kwargs)
        except acos_errors.Exists:
            acos_obj.update(**kwargs)

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
        try:
            c.client.slb.virtual_server.vport.delete(
                self.a10_driver.loadbalancer._name(listener.loadbalancer),
                self._meta_name(listener),
                protocol=openstack_mappings.vip_protocols(c, listener.protocol),
                port=listener.protocol_port)
        except acos_errors.NotFound:
            pass

        # clean up ssl template
        if listener.protocol and listener.protocol == constants.PROTOCOL_TERMINATED_HTTPS:
            try:
                c.client.slb.template.client_ssl.delete(listener.id)
            except acos_errors.NotFound:
                pass

    def delete(self, context, listener):
        with a10.A10DeleteContext(self, context, listener) as c:
            self._delete(c, context, listener)
