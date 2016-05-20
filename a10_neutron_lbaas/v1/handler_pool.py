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

from a10_neutron_lbaas.acos import openstack_mappings
import acos_client.errors as acos_errors
import handler_base_v1
import v1_context as a10

LOG = logging.getLogger(__name__)


class PoolHandler(handler_base_v1.HandlerBaseV1):

    def _set(self, set_method, c, context, pool):
        args = {'service_group': self.meta(pool, 'service_group', {})}

        set_method(
            self._meta_name(pool),
            protocol=openstack_mappings.service_group_protocol(c, pool['protocol']),
            lb_method=openstack_mappings.service_group_lb_method(c, pool['lb_method']),
            axapi_args=args)

    def create(self, context, pool):
        with a10.A10WriteStatusContext(self, context, pool, action='create') as c:
            try:
                self._set(c.client.slb.service_group.create,
                          c, context, pool)
            except acos_errors.Exists:
                pass

    def update(self, context, old_pool, pool):
        # id_func = lambda x: x.get("monitor_id")

        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c.client.slb.service_group.update,
                      c, context, pool)

    def delete(self, context, pool):
        with a10.A10DeleteContext(self, context, pool) as c:
            pool_id = pool.get("id")

            for member in pool['members']:
                m = self.neutron.member_get(context, member)
                self.a10_driver.member._delete(c, context, m)

            for hm in pool.get('health_monitors_status', []):
                z = self.neutron.hm_get(context, hm['monitor_id'])
                self.a10_driver.hm.dissociate(c, context, z, pool_id)

            if 'vip_id' in pool and pool['vip_id'] is not None:
                vip = self.neutron.vip_get(context, pool['vip_id'])
                self.a10_driver.vip._delete(c, context, vip)

            try:
                c.client.slb.service_group.delete(self._meta_name(pool))
            except (acos_errors.NotFound, acos_errors.NoSuchServiceGroup):
                pass

    def stats(self, context, pool_id):
        tenant_id = self.neutron.pool_get_tenant_id(context, pool_id)
        pool = {'id': pool_id, 'tenant_id': tenant_id}
        with a10.A10Context(self, context, pool) as c:
            try:
                vip_id = self.neutron.vip_get_id(context, pool['id'])
                vip = self.neutron.vip_get(context, vip_id)
                name = self.meta(vip, 'vip_name', vip['id'])
                r = c.client.slb.virtual_server.stats(name)
                return {
                    "bytes_in": r["virtual_server_stat"]["req_bytes"],
                    "bytes_out": r["virtual_server_stat"]["resp_bytes"],
                    "active_connections":
                        r["virtual_server_stat"]["cur_conns"],
                    "total_connections": r["virtual_server_stat"]["tot_conns"]
                }
            except Exception:
                return {
                    "bytes_in": 0,
                    "bytes_out": 0,
                    "active_connections": 0,
                    "total_connections": 0
                }
