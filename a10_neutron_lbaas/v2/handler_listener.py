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

import a10_neutron_lbaas.a10_exceptions as a10_ex
import a10_neutron_lbaas.a10_openstack_map as a10_os

import acos_client.errors as acos_errors
import handler_base
import v2_context as a10

LOG = logging.getLogger(__name__)


class ListenerHandler(handler_base.HandlerBaseV2):

    def _set(self, set_method, c, context, listener):
        status = c.client.slb.UP
        if not listener['admin_state_up']:
            status = c.client.slb.DOWN

        pool_name = self._pool_name(context, listener.default_pool)

        p = PersistHandler(c, context, listener, self._meta_name(listener))
        p.create()

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

        if vport_list[0]:
            vport_args = {'port': vport_list[0]}
        else:
            vport_args = {'port': self.meta(vip, 'port', {})}
        try:
            c.client.slb.virtual_server.vport.create(
                self._meta_name(listener),
                self._meta_name(listener) + '_VPORT',
                protocol=a10_os.vip_protocols(c, listener['protocol']),
                port=listener['protocol_port'],
                service_group_name=pool_name,
                s_pers_name=p.s_persistence(),
                c_pers_name=p.c_persistence(),
                status=status,
                axapi_args=vport_args)
        except acos_errors.Exists:
            pass


        # vport_list = [{}]
        # try:
        #     vip_args = {
        #         'virtual_server': self.meta(vip, 'virtual_server', {})
        #     }
        #     vport_list = vip_args['virtual_server'].pop('vport_list', [{}])
        #     c.client.slb.virtual_server.create(
        #         self._meta_name(vip),
        #         vip['address'],
        #         status,
        #         axapi_args=vip_args)
        # except acos_errors.Exists:
        #     pass

        # LOG.debug("VPORT_LIST = %s", vport_list)
        # try:
        #     if vport_list[0]:
        #         vport_args = {'port': vport_list[0]}
        #     else:
        #         vport_args = {'port': self.meta(vip, 'port', {})}
        #     c.client.slb.virtual_server.vport.create(
        #         self._meta_name(vip),
        #         self._meta_name(vip) + '_VPORT',
        #         protocol=a10_os.vip_protocols(c, vip['protocol']),
        #         port=vip['protocol_port'],
        #         service_group_name=pool_name,
        #         s_pers_name=p.s_persistence(),
        #         c_pers_name=p.c_persistence(),
        #         status=status,
        #         axapi_args=vport_args)
        # except acos_errors.Exists:
        #     pass

        # i = 1
        # for vport in vport_list[1:]:
        #     i += 1
        #     try:
        #         vport_args = {'port': vport}
        #         c.client.slb.virtual_server.vport.create(
        #             self._meta_name(vip),
        #             self._meta_name(vip) + '_VPORT' + str(i),
        #             protocol=a10_os.vip_protocols(c, vip['protocol']),
        #             port=vip['protocol_port'],
        #             service_group_name=pool_name,
        #             s_pers_name=p.s_persistence(),
        #             c_pers_name=p.c_persistence(),
        #             status=status,
        #             axapi_args=vport_args)
        #     except acos_errors.Exists:
        #         pass


    def create(self, context, listener):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            status = c.client.slb.UP
            if not vip['admin_state_up']:
                status = c.client.slb.DOWN

            pool_name = self._pool_name(context, vip['pool_id'])

            p = PersistHandler(c, context, vip, self._meta_name(vip))
            p.create()

            templates = self.meta(vip, "template", {})

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

            vport_list = [{}]
            try:
                vip_args = {
                    'virtual_server': self.meta(vip, 'virtual_server', {})
                }
                vport_list = vip_args['virtual_server'].pop('vport_list', [{}])
                c.client.slb.virtual_server.create(
                    self._meta_name(vip),
                    vip['address'],
                    status,
                    axapi_args=vip_args)
            except acos_errors.Exists:
                pass

            LOG.debug("VPORT_LIST = %s", vport_list)
            try:
                if vport_list[0]:
                    vport_args = {'port': vport_list[0]}
                else:
                    vport_args = {'port': self.meta(vip, 'port', {})}
                c.client.slb.virtual_server.vport.create(
                    self._meta_name(vip),
                    self._meta_name(vip) + '_VPORT',
                    protocol=a10_os.vip_protocols(c, vip['protocol']),
                    port=vip['protocol_port'],
                    service_group_name=pool_name,
                    s_pers_name=p.s_persistence(),
                    c_pers_name=p.c_persistence(),
                    status=status,
                    axapi_args=vport_args)
            except acos_errors.Exists:
                pass

            i = 1
            for vport in vport_list[1:]:
                i += 1
                try:
                    vport_args = {'port': vport}
                    c.client.slb.virtual_server.vport.create(
                        self._meta_name(vip),
                        self._meta_name(vip) + '_VPORT' + str(i),
                        protocol=a10_os.vip_protocols(c, vip['protocol']),
                        port=vip['protocol_port'],
                        service_group_name=pool_name,
                        s_pers_name=p.s_persistence(),
                        c_pers_name=p.c_persistence(),
                        status=status,
                        axapi_args=vport_args)
                except acos_errors.Exists:
                    pass

            self.hooks.after_vip_create(c, context, vip)

    def update(self, context, old_listener, listener):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            status = c.client.slb.UP
            if not vip['admin_state_up']:
                status = c.client.slb.DOWN

            pool_name = self._pool_name(context, vip['pool_id'])

            p = PersistHandler(c, context, vip, self._meta_name(vip))
            p.create()

            templates = self.meta(vip, "template", {})

            if 'client_ssl' in templates:
                args = {'client_ssl_template': templates['client_ssl']}
                c.client.slb.template.client_ssl.update(
                    '', '', '',
                    axapi_args=args)

            if 'server_ssl' in templates:
                args = {'server_ssl_template': templates['server_ssl']}
                c.client.slb.template.server_ssl.update(
                    '', '', '',
                    axapi_args=args)

            vport_args = {'port': self.meta(vip, 'port', {})}
            c.client.slb.virtual_server.vport.update(
                self._meta_name(vip),
                self._meta_name(vip) + '_VPORT',
                protocol=a10_os.vip_protocols(c, vip['protocol']),
                port=vip['protocol_port'],
                service_group_name=pool_name,
                s_pers_name=p.s_persistence(),
                c_pers_name=p.c_persistence(),
                status=status,
                axapi_args=vport_args)

    def _delete(self, c, context, listener):
        c.client.slb.virtual_server.delete(self._meta_name(listener))
        PersistHandler(c, context, listener, self._meta_name(listener)).delete()

    def delete(self, context, listener):
        with a10.A10DeleteContext(self, context, listener) as c:
            self._delete(c, context, listener)
