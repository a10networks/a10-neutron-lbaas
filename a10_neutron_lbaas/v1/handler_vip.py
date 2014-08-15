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

import a10_neutron_lbaas.a10_exceptions as a10_ex

import acos_client.errors as acos_errors
import handler_base
import v1_context as a10


class VipHandler(handler_base.HandlerBase):

    def _model_type(self):
        return 'vip'

    def _protocols(self, c):
        return {
            'TCP': c.client.slb.virtual_server.vport.TCP,
            'UDP': c.client.slb.virtual_server.vport.UDP,
            'HTTP': c.client.slb.virtual_server.vport.HTTP,
            'HTTPS': c.client.slb.virtual_server.vport.TCP
        }

    def create(self, context, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            status = c.client.slb.UP
            if not vip['admin_state_up']:
                status = c.client.slb.DOWN

            p = PersistHandler(c, context, vip)
            p.create()

            c.client.slb.virtual_server.create(
                vip['id'],
                vip['address'],
                status)

            c.client.slb.virtual_server.vport.create(
                vip['id'],
                vip['id'] + '_VPORT',
                protocol=self._protocols(c)[vip['protocol']],
                port=vip['protocol_port'],
                service_group_name=vip['pool_id'],
                s_pers_name=p.s_persistence(),
                c_pers_name=p.c_persistence(),
                status=status)

    def update(self, context, old_vip, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            status = c.client.slb.UP
            if not vip['admin_state_up']:
                status = c.client.slb.DOWN

            p = PersistHandler(c, context, vip)
            p.create()

            c.client.slb.virtual_server.vport.update(
                vip['id'],
                vip['id'] + '_VPORT',
                protocol=self._protocols(c)[vip['protocol']],
                port=vip['protocol_port'],
                service_group_name=vip['pool_id'],
                s_pers_name=p.s_persistence(),
                c_pers_name=p.c_persistence(),
                status=status)

    def _delete(self, c, context, vip):
        c.client.slb.virtual_server.delete(vip['id'])
        PersistHandler(c, context, vip).delete()

    def delete(self, context, vip):
        with a10.A10DeleteContext(self, context, vip) as c:
            self._delete(c, context, vip)


class PersistHandler(object):

    def __init__(self, c, context, vip):
        self.c = c
        self.context = context
        self.vip = vip
        self.c_pers = None
        self.s_pers = None
        self.name = vip['id']

        if vip.get('session_persistence', None) is not None:
            self.sp = vip['session_persistence']
            if self.sp['type'] == 'HTTP_COOKIE':
                self.c_pers = self.name
            elif self.sp['type'] == 'SOURCE_IP':
                self.s_pers = self.name
            else:
                raise a10_ex.UnsupportedFeature()
        else:
            self.sp = None

    def c_persistence(self):
        return self.c_pers

    def s_persistence(self):
        return self.s_pers

    def create(self):
        if self.sp is None:
            return

        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.create,
            'SOURCE_IP':
                self.c.client.slb.template.src_ip_persistence.create,
        }
        if self.sp['type'] in methods:
            try:
                methods[self.sp['type']](self.name)
            except acos_errors.Exists:
                pass

    def delete(self):
        if self.sp is None:
            return

        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.delete,
            'SOURCE_IP':
                self.c.client.slb.template.src_ip_persistence.delete,
        }
        if self.sp['type'] in methods:
            try:
                methods[self.sp['type']](self.name)
            except Exception:
                pass
