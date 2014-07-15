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

import a10_context as a10


class ListenerHandler(HandlerBase):

    def _persistence_get(self, c, context, listener):
        if not listener.pool or not listener.pool.sessionpersistence:
            return [None, None]

        sp = listener.pool.sessionpersistence
        name = listener.pool.id
        c_pers = None
        s_pers = None

        if sp.type == 'HTTP_COOKIE':
            c_pers = name
        elif sp.type == 'SOURCE_IP':
            s_pers = name

        return [c_pers, s_pers]

    def _set(self, c, set_method, context, listener):
        protocols = {
            'TCP': c.client.slb.virtual_server.vport.protocol.TCP,
            'UDP': c.client.slb.virtual_server.vport.protocol.UDP,
            'HTTP': c.client.slb.virtual_server.vport.protocol.HTTP,
            'HTTPS': c.client.slb.virtual_server.vport.protocol.HTTPS
        }

        status = c.slb.UP
        if not listener.admin_state_up:
            status = c.slb.DOWN

        pers = self._persistence_get(c, context, listener)

        set_method(listener.load_balancer_id, listener.id,
                   protocol=protocols[listener.protocol],
                   port=listener.port,
                   service_group_name=listener.pool_id,
                   s_pers_name=pers[1],
                   c_pers_name=pers[0],
                   status=status)

    def create(self, context, listener):
        if not listener.load_balancer:
            return

        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c, c.client.slb.virtual_server.vport.create, context,
                      listener)

    def _update(self, c, context, listener):
        self._set(c, c.client.slb.virtual_server.vport.update, context,
                  listener)

    def update(self, context, old_listener, listener):
        if not listener.load_balancer:
            return
            
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._update(c, context, listener)

    def delete(self, context, listener):
        if not listener.load_balancer:
            return
            
        with a10.A10DeleteContext(self, context, pool) as c:
            c.client.slb.virtual_server.vport.delete(
                listener.load_balancer_id,
                listener.id,
                protocol=protocols[listener.protocol],
                port=listener.port)
