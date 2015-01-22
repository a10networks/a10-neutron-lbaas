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

import acos_client.errors as acos_errors
import handler_base
import v1_context as a10

LOG = logging.getLogger(__name__)


class PoolHandler(handler_base.HandlerBase):

    def _model_type(self):
        return 'pool'

    def _get_hm(self, context, hm_id):
        return self.openstack_driver._pool_get_hm(context, hm_id)

    def _get_member(self, context, member_id):
        return self.openstack_driver._member_get(context, member_id)

    def _get_tenant_id(self, context, pool_id):
        return self.openstack_driver._pool_get_tenant_id(context, pool_id)

    def _get_vip_id(self, context, pool_id):
        return self.openstack_driver._pool_get_vip_id(context, pool_id)

    def _get_vip(self, context, vip_id):
        return self.openstack_driver.plugin.get_vip(context, vip_id)

    def _meta_name(self, pool):
        return self.meta(pool, 'name', pool['id'])

    def _set(self, set_method, c, context, pool):
        z = c.client.slb.service_group
        lb_methods = {
            'ROUND_ROBIN': z.ROUND_ROBIN,
            'LEAST_CONNECTIONS': z.LEAST_CONNECTION,
            'SOURCE_IP': z.WEIGHTED_LEAST_CONNECTION,
            'WEIGHTED_ROUND_ROBIN': z.WEIGHTED_ROUND_ROBIN,
            'WEIGHTED_LEAST_CONNECTION': z.WEIGHTED_LEAST_CONNECTION,
            'LEAST_CONNECTION_ON_SERVICE_PORT':
                z.LEAST_CONNECTION_ON_SERVICE_PORT,
            'WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT':
                z.WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT,
            'FAST_RESPONSE_TIME': z.FAST_RESPONSE_TIME,
            'LEAST_REQUEST': z.LEAST_REQUEST,
            'STRICT_ROUND_ROBIN': z.STRICT_ROUND_ROBIN,
            'STATELESS_SOURCE_IP_HASH': z.STATELESS_SOURCE_IP_HASH,
            'STATELESS_DESTINATION_IP_HASH': z.STATELESS_DESTINATION_IP_HASH,
            'STATELESS_SOURCE_DESTINATION_IP_HASH':
                z.STATELESS_SOURCE_DESTINATION_IP_HASH,
            'STATELESS_PER_PACKET_ROUND_ROBIN':
                z.STATELESS_PER_PACKET_ROUND_ROBIN,
        }
        protocols = {
            'HTTP': z.TCP,
            'HTTPS': z.TCP,
            'TERMINATED_HTTPS': z.TCP,
            'TCP': z.TCP,
            'UDP': z.UDP
        }
        args = {'service_group': self.meta(pool, 'service_group', {})}

        set_method(self._meta_name(pool),
                   protocol=protocols[pool['protocol']],
                   lb_method=lb_methods[pool['lb_method']],
                   axapi_args=args)

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
            for member in pool['members']:
                m = self._get_member(context, member)
                self.a10_driver.member._delete(c, context, m)

            for hm in pool['health_monitors_status']:
                z = self._get_hm(context, hm['monitor_id'])
                self.a10_driver.hm._delete(c, context, z)

            if 'vip_id' in pool and pool['vip_id'] is not None:
                vip = self._get_vip(context, pool['vip_id'])
                self.a10_driver.vip._delete(c, context, vip)

            c.client.slb.service_group.delete(self._meta_name(pool))

    def stats(self, context, pool_id):
        tenant_id = self._get_tenant_id(context, pool_id)
        pool = {'id': pool_id, 'tenant_id': tenant_id}
        with a10.A10Context(self, context, pool) as c:
            try:
                vip_id = self._get_vip(context, pool['id'])
                vip = self._get_vip(context, vip_id)
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
