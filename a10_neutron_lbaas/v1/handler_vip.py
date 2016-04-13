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
from a10_neutron_lbaas.acos import openstack_mappings

import acos_client.errors as acos_errors
import handler_base_v1
import v1_context as a10


LOG = logging.getLogger(__name__)


class VipHandler(handler_base_v1.HandlerBaseV1):

    def vport_meta(self, vip):
        """Get the vport meta, no matter which name was used"""
        vport_meta = self.meta(vip, 'vport', None)
        if vport_meta is None:
            vport_meta = self.meta(vip, 'port', {})
        return vport_meta

    def create(self, context, vip):
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

            vport_list = None
            try:
                vip_meta = self.meta(vip, 'virtual_server', {})
                vport_list = vip_meta.pop('vport_list', None)

                c.client.slb.virtual_server.create(
                    self._meta_name(vip),
                    vip['address'],
                    status,
                    vrid=c.device_cfg.get('default_virtual_server_vrid'),
                    axapi_body=vip_meta)
            except acos_errors.Exists:
                pass

            LOG.debug("VPORT_LIST = %s", vport_list)
            if vport_list is None:
                vport_list = [self.vport_meta(vip)]
            for vport, i in zip(vport_list, range(len(vport_list))):
                try:
                    vport_name = str(i) if i else ''

                    c.client.slb.virtual_server.vport.create(
                        self._meta_name(vip),
                        self._meta_name(vip) + '_VPORT' + vport_name,
                        protocol=openstack_mappings.vip_protocols(c, vip['protocol']),
                        port=vip['protocol_port'],
                        service_group_name=pool_name,
                        s_pers_name=p.s_persistence(),
                        c_pers_name=p.c_persistence(),
                        status=status,
                        autosnat=c.device_cfg.get('autosnat'),
                        ipinip=c.device_cfg.get('ipinip'),
                        axapi_body=vport)
                except acos_errors.Exists:
                    pass

            self.hooks.after_vip_create(c, context, vip)

    def update(self, context, old_vip, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            status = c.client.slb.UP
            if not vip['admin_state_up']:
                status = c.client.slb.DOWN

            pool_name = self._pool_name(context, vip['pool_id'])

            p = PersistHandler(c, context, vip, self._meta_name(vip), old_vip)
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

            vport_meta = self.vport_meta(vip)

            c.client.slb.virtual_server.vport.update(
                self._meta_name(vip),
                self._meta_name(vip) + '_VPORT',
                protocol=openstack_mappings.vip_protocols(c, vip['protocol']),
                port=vip['protocol_port'],
                service_group_name=pool_name,
                s_pers_name=p.s_persistence(),
                c_pers_name=p.c_persistence(),
                status=status,
                autosnat=c.device_cfg.get('autosnat'),
                ipinip=c.device_cfg.get('ipinip'),
                axapi_body=vport_meta)

            self.hooks.after_vip_update(c, context, vip)

    def _delete(self, c, context, vip):
        try:
            c.client.slb.virtual_server.delete(self._meta_name(vip))
        except acos_errors.NotFound:
            pass

        PersistHandler(c, context, vip, self._meta_name(vip)).delete()

    def delete(self, context, vip):
        with a10.A10DeleteContext(self, context, vip) as c:
            self._delete(c, context, vip)
            self.hooks.after_vip_delete(c, context, vip)


class PersistHandler(object):

    def __init__(self, c, context, vip, vip_name, old_vip=None):
        self.c = c
        self.context = context
        self.vip = vip
        self.c_pers = None
        self.s_pers = None
        self.name = vip_name
        self.old_vip = old_vip

        self.sp_obj_dict = {
            'HTTP_COOKIE': "cookie_persistence",
            'SOURCE_IP': "src_ip_persistence",
        }

        self.sp = vip.get("session_persistence")

        if self.sp is not None:
            if self.sp['type'] == 'HTTP_COOKIE':
                self.c_pers = self.name
            elif self.sp['type'] == 'SOURCE_IP':
                self.s_pers = self.name
            else:
                raise a10_ex.UnsupportedFeature()

    def c_persistence(self):
        return self.c_pers

    def s_persistence(self):
        return self.s_pers

    def create(self):
        if self.old_vip is not None:
            vip_sp = self.old_vip.get("session_persistence")
            if vip_sp is not None:

                try:
                    vip_sp_type = vip_sp.get("type")
                    m = getattr(self.c.client.slb.template, self.sp_obj_dict[vip_sp_type])
                    m.delete(self.old_vip.get("id"))
                except acos_errors.NotExists:
                    pass

        if self.sp is not None:
            sp_type = self.sp.get("type")
            if sp_type is not None and sp_type in self.sp_obj_dict:
                try:
                    m = getattr(self.c.client.slb.template, self.sp_obj_dict[sp_type])
                    m.create(self.name)
                except acos_errors.Exists:
                    pass

    def delete(self):

        if self.sp is None:
            return

        sp_type = self.sp.get("type")
        if sp_type in self.sp_obj_dict.keys():
            try:
                m = getattr(self.c.client.slb.template, self.sp_obj_dict[sp_type])
                m.delete(self.name)

            except Exception as e:
                LOG.exception(e)
