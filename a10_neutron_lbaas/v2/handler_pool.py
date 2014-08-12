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
import v2_context as a10


class PoolHandler(handler_base.HandlerBase):

    def _set(self, c, set_method, context, pool):
        lb_methods = {
            'ROUND_ROBIN': c.client.slb.service_group.ROUND_ROBIN,
            'LEAST_CONNECTIONS': c.client.slb.service_group.LEAST_CONNECTION,
            'SOURCE_IP': c.client.slb.service_group.WEIGHTED_LEAST_CONNECTION
        }
        protocols = {
            'HTTP': c.client.slb.service_group.TCP,
            'HTTPS': c.client.slb.service_group.TCP,
            'TCP': c.client.slb.service_group.TCP,
            'UDP': c.client.slb.service_group.UDP
        }

        set_method(pool.id,
                   protocol=protocols[pool.protocol],
                   lb_method=lb_methods[pool.lb_algorithm])

        if pool.sessionpersistence:
            PersistenceHandler(self, c, context, pool).create()

    def create(self, context, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c, c.client.slb.service_group.create, context, pool)

    def update(self, context, old_pool, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c, c.client.slb.service_group.update, context, pool)

    def delete(self, context, pool):
        with a10.A10DeleteContext(self, context, pool) as c:
            for member in pool.members:
                self.a10_driver.member._delete(c, context, member)

            if pool.healthmonitor:
                self.a10_driver.hm._delete(c, context, pool.healthmonitor)

            c.client.slb.service_group.delete(pool.id)

            if pool.sessionpersistence:
                PersistenceHandler(self, c, context, pool).delete()


class PersistenceHandler(object):

    def __init__(self, pool_handler, c, context, pool):
        self.pool_handler = pool_handler
        self.c = c
        self.context = context
        self.pool = pool
        self.sp = pool.sessionpersistence
        self.name = pool.id

    def create(self):
        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.create,
            'SOURCE_IP':
                self.c.client.slb.template.src_ip_persistence.create,
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
                self.c.client.slb.template.src_ip_persistence.delete,
        }
        if self.sp.type in methods:
            try:
                methods[self.sp.type](self.name)
            except Exception:
                pass

        if self.pool.listener:
            self.pool_handler.a10_driver.listener._update(self.c, self.context,
                                                          self.pool.listener)
