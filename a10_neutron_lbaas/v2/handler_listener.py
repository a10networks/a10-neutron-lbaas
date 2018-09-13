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
from a10_neutron_lbaas.neutron_ext.db.certificate_db \
    import A10CertificateDbMixin as A10CertificateDb
import a10_neutron_lbaas.v2.wrapper_certmgr as certwrapper
import handler_base_v2
import handler_persist
import v2_context as a10


LOG = logging.getLogger(__name__)


class ListenerHandler(handler_base_v2.HandlerBaseV2):

    def __init__(self, a10_driver, openstack_manager, neutron=None, barbican_client=None,
                 cert_db=None):
        super(ListenerHandler, self).__init__(a10_driver, openstack_manager, neutron)
        self._barbican_client = barbican_client
        self._cert_db = cert_db

    @property
    def cert_db(self):
        if self._cert_db is None:
            self._cert_db = A10CertificateDb()
        return self._cert_db

    @property
    def barbican_client(self):
        if self._barbican_client is None:
            self._barbican_client = certwrapper.CertManagerWrapper(handler=self)
        return self._barbican_client

    def _set(self, set_method, c, context, listener):

        status = c.client.slb.UP
        if not listener.admin_state_up:
            status = c.client.slb.DOWN

        templates = self.meta(listener, "template", {})

        server_args = {}
        cert_data = dict()
        template_args = {}
        protocol = openstack_mappings.vip_protocols(c, listener.protocol)
        binding = None
        os_name = listener.name or None
        # Try Barbican first.  TERMINATED HTTPS requires a default TLS container ID that is
        # checked by the API so we can't fake it out.
        if listener.protocol and listener.protocol == constants.PROTOCOL_TERMINATED_HTTPS:
            if self._set_terminated_https_values(listener, c, cert_data):
                templates["client_ssl"] = {}
                template_name = str(cert_data.get('template_name') or '')
                key_passphrase = str(cert_data.get('key_pass') or '')
                cert_filename = str(cert_data.get('cert_filename') or '')
                key_filename = str(cert_data.get('key_filename') or '')
            else:
                LOG.error("Could not created terminated HTTPS endpoint.")
        # Else, set it up as an HTTP endpoint and attach the A10 cert data.
        elif (self.a10_driver.config.get('use_database') and listener.protocol and
              listener.protocol in [constants.PROTOCOL_HTTPS,
                                    constants.PROTOCOL_HTTP,
                                    constants.PROTOCOL_TCP]):
            try:
                binding = self.cert_db.get_binding_for_listener(context, listener.id)
            except Exception as ex:
                LOG.exception(ex)

            if binding:
                # if the binding is being deleted and the listener wasn't created as https,
                # remove the https port to make room for the original port
                if binding.status == constants.STATUS_DELETING:

                    if (protocol != c.client.slb.virtual_server.vport.HTTPS):
                        self._delete_listener(c, context, listener,
                                              c.client.slb.virtual_server.vport.HTTPS)
                        set_method = c.client.slb.virtual_server.vport.create
                elif self._set_a10_https_values(listener, c, cert_data, binding):
                    # If the binding hasn't been created and the port isn't https
                    # remove the port and re-create it as https.
                    if (binding.status == constants.STATUS_CREATING and
                            protocol != c.client.slb.virtual_server.vport.HTTPS):

                        self._delete_listener(c, context, listener, protocol)
                        set_method = c.client.slb.virtual_server.vport.create

                    protocol = c.client.slb.virtual_server.vport.HTTPS
                    templates["client_ssl"] = {}
                    template_name = str(cert_data.get('template_name') or '')
                    key_passphrase = str(cert_data.get('key_pass') or '')
                    cert_filename = str(cert_data.get('cert_filename') or '')
                    key_filename = str(cert_data.get('key_filename') or '')
                    template_args["template_client_ssl"] = template_name

        if 'client_ssl' in templates:
            template_args["template_client_ssl"] = template_name
            try:
                c.client.slb.template.client_ssl.create(
                    template_name,
                    cert=cert_filename,
                    key=key_filename,
                    passphrase=key_passphrase)
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
                    passphrase=key_passphrase,
                    axapi_args=server_args)
            except acos_errors.Exists:
                c.client.slb.template.server_ssl.update(template_name,
                                                        cert_filename,
                                                        key_filename,
                                                        passphrase=key_passphrase,
                                                        axapi_args=server_args)

        try:
            pool_name = self._pool_name(context, pool_id=listener.default_pool_id)
        except Exception:
            pool_name = None

        persistence = handler_persist.PersistHandler(
            c, context, listener.default_pool)

        # This doesn't do anything anymore.
        vport_meta = self.meta(listener.loadbalancer, 'vip_port', {})
        template_args.update(**self._get_vport_defaults(c, os_name))

        vport_defaults = self._get_vport_defaults(c, os_name)

        # ADD A CONDITION TO VPORT DEFAULTS TO FIX THIS
        # EXAMPLE:
        # "condition": {"field": "protocol", "op": "=", "value": "http"}}
        if "ha-conn-mirror" in vport_defaults and protocol.lower() not in ("tcp", "udp"):
            del vport_defaults["ha-conn-mirror"]

        if "ha-conn-mirror" in template_args and protocol.lower() not in ("tcp", "udp"):
            del template_args["ha-conn-mirror"]

        if "template-http" in vport_defaults and protocol.lower() not in ("http", "https"):
            del vport_defaults["template-http"]

        if "template-http" in template_args and protocol.lower() not in ("http", "https"):
            del template_args["template-http"]

        if "no-dest-nat" in vport_defaults and protocol.lower() in ("http", "https"):
            del vport_defaults["no-dest-nat"]

        if "no-dest-nat" in template_args and protocol.lower() in ("http", "https"):
            del template_args["no-dest-nat"]

        try:

            set_method(
                self.a10_driver.loadbalancer._name(listener.loadbalancer),
                self._meta_name(listener),
                protocol=protocol,
                port=listener.protocol_port,
                service_group_name=pool_name,
                s_pers_name=persistence.s_persistence(),
                c_pers_name=persistence.c_persistence(),
                status=status,
                autosnat=c.device_cfg.get('autosnat'),
                ipinip=c.device_cfg.get('ipinip'),
                source_nat_pool=c.device_cfg.get('source_nat_pool'),
                # Device-level defaults
                vport_defaults=vport_defaults,
                axapi_body=vport_meta,
                **template_args)
        except acos_errors.Exists:
            pass

    def _set_terminated_https_values(self, listener, c, cert_data):
        is_success = False
        container = None

        c_id = listener.default_tls_container_id if listener.default_tls_container_id else None

        # if there's a barbican container ID, check there.
        if c_id:
            try:
                container = self.barbican_client.get_certificate(c_id, check_only=True,
                                                                 project_id=c.tenant_id)
            except Exception as ex:
                container = None
                LOG.error("Exception encountered retrieving TLS Container %s" % c_id)
                LOG.exception(ex)

            if container:
                base_name = getattr(
                    getattr(container, '_cert_container', None), 'name', '') or c_id

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
            LOG.error("default_tls_container_id unspecified for listener.")
        return is_success

    def _set_a10_https_values(self, listener, c, cert_data, binding):
        LOG.info("default_tls_container_id unspecified for listener. Checking A10 DB.")
        is_success = False

        cert_data["cert_content"] = binding.certificate.cert_data or None
        cert_data["key_content"] = binding.certificate.key_data or None
        cert_data["key_pass"] = binding.certificate.password or None

        if len(cert_data["cert_content"]) > 1:
            base_name = listener.id
            cert_data["template_name"] = base_name

            cert_data["cert_filename"] = "{0}cert.pem".format(base_name)

            self._acos_create_or_update(c.client.file.ssl_cert,
                                        file=cert_data["cert_filename"],
                                        cert=cert_data["cert_content"],
                                        size=len(cert_data["cert_content"]),
                                        action="import", certificate_type="pem")

            if len(cert_data.get("key_content") or "") > 0:
                cert_data["key_filename"] = "{0}key.pem".format(base_name)
                self._acos_create_or_update(c.client.file.ssl_key,
                                            file=cert_data["key_filename"],
                                            cert=cert_data["key_content"],
                                            size=len(cert_data["key_content"]),
                                            action="import")

            is_success = True

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

    def _delete_listener(self, c, context, listener, protocol):
        try:
            c.client.slb.virtual_server.vport.delete(
                self.a10_driver.loadbalancer._name(listener.loadbalancer),
                self._meta_name(listener),
                protocol=protocol,
                port=listener.protocol_port)
        except acos_errors.NotFound:
            pass

    def _delete(self, c, context, listener):
        # First, remove any existing cert bindings and set the correct protocol for delete.
        # Existence of bindings means the vport has been re-created as https.
        protocol = openstack_mappings.vip_protocols(c, listener.protocol)

        if self.a10_driver.config.use_database and self._remove_existing_bindings(
                c, context, listener):
                protocol = c.client.slb.virtual_server.vport.HTTPS

        # Regular delete, use regular protocol mapping.
        self._delete_listener(
            c, context, listener, protocol)

        # clean up ssl template
        if listener.protocol and listener.protocol == constants.PROTOCOL_TERMINATED_HTTPS:
            try:
                c.client.slb.template.client_ssl.delete(listener.id)
            except acos_errors.NotFound:
                pass

    def delete(self, context, listener):
        with a10.A10DeleteContext(self, context, listener) as c:
            self._delete(c, context, listener)

    def _remove_existing_bindings(self, c, context, listener):
        binding = None

        try:
            binding = self.cert_db.get_binding_for_listener(context, listener.id)
        except Exception as ex:
            LOG.exception(ex)
        # if we have bindings, remove them
        if binding is not None:
            try:
                self.cert_db.delete_a10_certificate_binding(context, binding.id)
            except Exception as ex:
                LOG.exception(ex)
        return binding

    def _get_global_vport_defaults(self, c):
        return c.a10_driver.config.get_vport_defaults()

    def _get_device_vport_defaults(self, c):
        return c.device_cfg.get("vport_defaults")

    def _get_vport_defaults(self, c, vport_name):
        rv = {}
        # Device-specific defaults have precedence over global
        rv.update(self._get_global_vport_defaults(c))
        rv.update(self._get_device_vport_defaults(c))
        if vport_name and len(vport_name) > 0:
            self._get_name_matches(rv, vport_name, self._get_expressions(c))
        return rv

    def _get_expressions(self, c):
        rv = {}
        rv = c.a10_driver.config.get_vport_expressions()
        return rv

