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

        set_method(pool['id'],
                   protocol=protocols[pool['protocol']],
                   lb_method=lb_methods[pool['lb_method']])

    def create(self, context, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            try:
                self._set(c, c.client.slb.service_group.create, context, pool)
            except acos_errors.Exists:
                pass

    def update(self, context, old_pool, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c, c.client.slb.service_group.update, context, pool)

    def delete(self, context, pool):
        with a10.A10DeleteContext(self, context, pool) as c:
            LOG.debug("POOL = %s", pool)
            for member in pool['members']:
                m = self._get_member(context, member)
                LOG.debug("MEMBER = %s", m)
                self.a10_driver.member._delete(c, context, m)

            for hm in pool['health_monitors_status']:
                z = self._get_hm(context, hm['monitor_id'])
                LOG.debug("HM = %s", z)
                self.a10_driver.hm._delete(c, context, z)

            if 'vip_id' in pool and pool['vip_id'] is not None:
                vip = self._get_vip(context, pool['vip_id'])
                self.a10_driver.vip._delete(c, context, vip)

            c.client.slb.service_group.delete(pool['id'])

    def stats(self, context, pool_id):
        tenant_id = self._get_tenant_id(context, pool_id)
        pool = {'id': pool_id, 'tenant_id': tenant_id}
        with a10.A10Context(self, context, pool) as c:
            try:
                vip_id = self._get_vip_id(context, pool_id)
                r = c.client.slb.virtual_server.stats(vip_id)
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
