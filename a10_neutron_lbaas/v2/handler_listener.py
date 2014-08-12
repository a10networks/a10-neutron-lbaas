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

import handler_base
import v2_context as a10


class ListenerHandler(handler_base.HandlerBase):

    def _protocols(self, c):
        return {
            'TCP': c.client.slb.virtual_server.vport.TCP,
            'UDP': c.client.slb.virtual_server.vport.UDP,
            'HTTP': c.client.slb.virtual_server.vport.HTTP,
            'HTTPS': c.client.slb.virtual_server.vport.TCP
        }

    def _persistence_get(self, c, context, listener):
        if (not listener.default_pool or
           not listener.default_pool.sessionpersistence):
            return [None, None]

        sp = listener.default_pool.sessionpersistence
        name = listener.default_pool.id
        c_pers = None
        s_pers = None

        if sp.type == 'HTTP_COOKIE':
            c_pers = name
        elif sp.type == 'SOURCE_IP':
            s_pers = name
        else:
            raise a10_ex.UnsupportedFeature()

        return [c_pers, s_pers]

    def _set(self, c, set_method, context, listener):
        status = c.client.slb.UP
        if not listener.admin_state_up:
            status = c.client.slb.DOWN

        pers = self._persistence_get(c, context, listener)

        set_method(listener.loadbalancer.id, listener.id,
                   protocol=self._protocols(c)[listener.protocol],
                   port=listener.port,
                   service_group_name=listener.default_pool.id,
                   s_pers_name=pers[1],
                   c_pers_name=pers[0],
                   status=status)

    def _create(self, c, context, listener):
        self._set(c, c.client.slb.virtual_server.vport.create, context,
                  listener)

    def create(self, context, listener):
        if not listener.loadbalancer or not listener.default_pool:
            return

        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._create(c, context, listener)

    def _update(self, c, context, listener):
        self._set(c, c.client.slb.virtual_server.vport.update, context,
                  listener)

    def update(self, context, old_listener, listener):
        if not listener.loadbalancer or not listener.default_pool:
            return

        with a10.A10WriteStatusContext(self, context, listener) as c:
            self._update(c, context, listener)

    def delete(self, context, listener):
        if not listener.loadbalancer:
            return

        with a10.A10DeleteContext(self, context, listener) as c:
            c.client.slb.virtual_server.vport.delete(
                listener.loadbalancer.id,
                listener.id,
                protocol=self._protocols(c)[listener.protocol],
                port=listener.port)
