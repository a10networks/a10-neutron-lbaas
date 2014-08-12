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


        # if pool.sessionpersistence:
        #     PersistenceHandler(self, c, context, pool).create()



class VipHandler(handler_base.HandlerBase):

    def create(self, context, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:


    def create_vip(self, context, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            raise "todo"

        # s_pers, c_pers, status = self._setup_vip_args(a10, vip)

        # try:
        #     a10.virtual_server_create(vip['id'], vip['address'],
        #                               vip['protocol'], vip['protocol_port'],
        #                               vip['pool_id'],
        #                               s_pers, c_pers, status)
        #     self._active(context, lb_db.Vip, vip['id'])

        # except Exception:
        #     self._failed(context, lb_db.Vip, vip['id'])
        #     raise a10_ex.VipCreateError(vip=vip['id'])


    def update_vip(self, context, old_vip, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:
            raise "todo"

        # s_pers, c_pers, status = self._setup_vip_args(a10, vip)

        # try:
        #     a10.virtual_port_update(vip['id'], vip['protocol'],
        #                             vip['pool_id'],
        #                             s_pers, c_pers, status)
        #     self._active(context, lb_db.Vip, vip['id'])

        # except Exception:
        #     self._failed(context, lb_db.Vip, vip['id'])
        #     raise a10_ex.VipUpdateError(vip=vip['id'])



    def delete_vip(self, context, vip):
        with a10.A10DeleteContext(self, context, vip) as c:
            raise "todo"
            c.client.slb.virtual_server.delete(vip['id'])

        # try:
        #     if vip['session_persistence'] is not None:
        #         a10.persistence_delete(vip['session_persistence']['type'],
        #                                vip['id'])
        # except Exception:
        #     pass

        # try:
        #     a10.virtual_server_delete(vip['id'])
        #     self.plugin._delete_db_vip(context, vip['id'])
        # except Exception:
        #     self._failed(context, lb_db.Vip, vip['id'])
        #     raise a10_ex.VipDeleteError(vip=vip['id'])

    # def _persistence_create(self, a10, vip):
    #     persist_type = vip['session_persistence']['type']
    #     name = vip['id']

    #     try:
    #         if a10.persistence_exists(persist_type, name):
    #             return name
    #         a10.persistence_create(persist_type, name)
    #     except Exception:
    #         raise a10_ex.TemplateCreateError(template=name)

    #     return name

    # def _setup_vip_args(self, a10, vip):
    #     s_pers = None
    #     c_pers = None
    #     LOG.debug("_setup_vip_args vip=%s", vip)
    #     if ('session_persistence' in vip and
    #             vip['session_persistence'] is not None):
    #         LOG.debug("creating persistence template")
    #         pname = self._persistence_create(a10, vip)
    #         if vip['session_persistence']['type'] is "HTTP_COOKIE":
    #             c_pers = pname
    #         elif vip['session_persistence']['type'] == "SOURCE_IP":
    #             s_pers = pname
    #     status = 1
    #     if vip['admin_state_up'] is False:
    #         status = 0
    #     LOG.debug("_setup_vip_args = %s, %s, %d", s_pers, c_pers, status)
    #     return s_pers, c_pers, status




class LoadBalancerHandler(handler_base.HandlerBase):

    def _set(self, c, set_method, context, load_balancer):
        status = c.client.slb.UP
        if not load_balancer.admin_state_up:
            status = c.client.slb.DOWN

        set_method(load_balancer.id, load_balancer.address, status)

    def create(self, context, load_balancer):
        with a10.A10WriteStatusContext(self, context, load_balancer) as c:
            self._set(c, c.client.slb.virtual_server.create, context,
                      load_balancer)

            for listener in load_balancer.listeners:
                try:
                    self.a10_driver.listener._create(c, context, listener)
                except acos_errors.Exists:
                    pass

    def update(self, context, old_load_balancer, load_balancer):
        with a10.A10WriteStatusContext(self, context, load_balancer) as c:
            self._set(c, c.client.slb.virtual_server.update, context,
                      load_balancer)

    def delete(self, context, load_balancer):
        with a10.A10DeleteContext(self, context, load_balancer) as c:
            c.client.slb.virtual_server.delete(load_balancer.id)


class ListenerHandler(handler_base.HandlerBase):

    def _protocols(self, c):
        return {
            'TCP': c.client.slb.virtual_server.vport.protocol.TCP,
            'UDP': c.client.slb.virtual_server.vport.protocol.UDP,
            'HTTP': c.client.slb.virtual_server.vport.protocol.HTTP,
            'HTTPS': c.client.slb.virtual_server.vport.protocol.HTTPS
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

class PersistenceHandler(object):

    def __init__(self, pool_handler, c, context, pool):
        self.pool_handler = pool_handler
        self.c = c
        self.context = context
        self.pool = pool
        self.sp = pool.sessionpersistence
        self.name = pool.id

        self.c_pers = None
        self.s_pers = None

        if sp.type == 'HTTP_COOKIE':
            self.c_pers = pool['id']
        elif sp.type == 'SOURCE_IP':
            self.s_pers = pool['id']
        else:
            raise a10_ex.UnsupportedFeature()

    def c_pers(self):
        return self.c_pers

    def s_pers(self):
        return self.s_pers

    def create(self):
        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.create,
            'SOURCE_IP':
                self.c.client.slb.template.source_ip_persistence.create,
        }
        if self.sp.type in methods:
            try:
                methods[self.sp.type](self.name)
            except acos_errors.Exists:
                pass
        else:
            raise a10_ex.UnsupportedFeature()

        if self.pool.listener:
            self.pool_handler.a10_driver.listener._update(self.c, self.context,
                                                          self.pool.listener)

    def delete(self):
        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.delete,
            'SOURCE_IP':
                self.c.client.slb.template.source_ip_persistence.delete,
        }
        if self.sp.type in methods:
            try:
                methods[self.sp.type](self.name)
            except Exception:
                pass

        if self.pool.listener:
            self.pool_handler.a10_driver.listener._update(self.c, self.context,
                                                          self.pool.listener)
