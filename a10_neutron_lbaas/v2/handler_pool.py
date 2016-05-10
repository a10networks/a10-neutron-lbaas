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

import copy
import logging

from a10_neutron_lbaas import a10_openstack_map as a10_os
import acos_client.errors as acos_errors
import handler_base_v2
import handler_persist
import v2_context as a10

LOG = logging.getLogger(__name__)


class PoolHandler(handler_base_v2.HandlerBaseV2):

    def _set(self, set_method, c, context, pool):
        p = handler_persist.PersistHandler(c, context, pool)
        p.create()

        args = {'service_group': self.meta(pool, 'service_group', {})}
        set_method(
            self._meta_name(pool),
            protocol=a10_os.service_group_protocol(c, pool.protocol),
            lb_method=a10_os.service_group_lb_method(c, pool.lb_algorithm),
            axapi_args=args)

        # session persistence might need a vport update
        if pool.listener:
            pool.listener.default_pool_id = pool.listener.default_pool_id or pool.id
            self.a10_driver.listener._update(c, context, pool.listener)

    def _create(self, c, context, pool):
        try:
            self._set(c.client.slb.service_group.create,
                      c, context, pool)
        except acos_errors.Exists:
            pass

    def create(self, context, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            try:
                self._set(c.client.slb.service_group.create,
                          c, context, pool)
            except acos_errors.Exists:
                pass

    def update(self, context, old_pool, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c.client.slb.service_group.update,
                      c, context, pool)

    def delete(self, context, pool):
        with a10.A10DeleteContext(self, context, pool) as c:
            for member in pool.members:
                LOG.debug("handler_pool.delete(): removing member {0} from pool {1}".format(member, member.pool_id))
                self.a10_driver.member._delete(c, context, member)

            LOG.debug("handler_pool.delete(): Checking pool health monitor...")
            if pool.healthmonitor:
                # The pool.healthmonitor we get doesn't have a pool
                # Make a new one with the hm as the root
                hm = copy.copy(pool.healthmonitor)
                hm.pool = copy.copy(pool)
                hm.pool.healthmonitor = None
                LOG.debug("handler_pool.delete(): HM: %s" % hm)
                self.a10_driver.hm._delete(c, context, hm)

            try:
                c.client.slb.service_group.delete(self._meta_name(pool))
            except (acos_errors.NotFound, acos_errors.NoSuchServiceGroup):
                pass

            handler_persist.PersistHandler(
                c, context, pool, self._meta_name(pool)).delete()
