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

import a10_neutron_lbaas.a10_openstack_map as a10_os

import acos_client.errors as acos_errors
import handler_base_v2
import handler_persist
import v2_context as a10

LOG = logging.getLogger(__name__)


class ListenerHandler(handler_base_v2.HandlerBaseV2):

    def _set(self, set_method, c, context, listener):
        status = c.client.slb.UP
        if not listener.admin_state_up:
            status = c.client.slb.DOWN

        templates = self.meta(listener, "template", {})

        if 'client_ssl' in templates:
            args = {'client_ssl_template': templates['client_ssl']}
            try:
                c.client.slb.template.client_ssl.create(
                    '', '', '',
                    axapi_args=args)
            except acos_errors.Exists:
                pass

        if 'server_ssl' in templates:
            args = {'server_ssl_template': templates['server_ssl']}
            try:
                c.client.slb.template.server_ssl.create(
                    '', '', '',
                    axapi_args=args)
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
                protocol=a10_os.vip_protocols(c, listener.protocol),
                port=listener.protocol_port,
                service_group_name=pool_name,
                s_pers_name=persistence.s_persistence(),
                c_pers_name=persistence.c_persistence(),
                status=status,
                axapi_args=vport_args)
        except acos_errors.Exists:
            pass

    def create(self, context, listener):
        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._set(c.client.slb.virtual_server.vport.create, c, context, listener)

    def _update(self, c, context, listener):
        self._set(c.client.slb.virtual_server.vport.update, c, context, listener)

    def update(self, context, old_listener, listener):
        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._update(c, context, listener)

    def _delete(self, c, context, listener):
        c.client.slb.virtual_server.vport.delete(
            self.a10_driver.loadbalancer._name(listener.loadbalancer),
            self._meta_name(listener),
            protocol=a10_os.vip_protocols(c, listener.protocol),
            port=listener.protocol_port)

    def delete(self, context, listener):
        with a10.A10DeleteContext(self, context, listener) as c:
            self._delete(c, context, listener)
