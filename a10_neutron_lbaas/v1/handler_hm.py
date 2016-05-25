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

import acos_client.errors as acos_errors
import logging

from a10_neutron_lbaas.acos import openstack_mappings
import handler_base_v1
import v1_context as a10


LOG = logging.getLogger(__name__)


class HealthMonitorHandler(handler_base_v1.HandlerBaseV1):

    def _name(self, hm):
        return hm['id'][0:28]

    def _set(self, c, set_method, context, hm):
        hm_name = self._meta_name(hm)
        method = None
        url = None
        expect_code = None
        if hm['type'] in ['HTTP', 'HTTPS']:
            method = hm['http_method']
            url = hm['url_path']
            expect_code = hm['expected_codes']

        args = self.meta(hm, 'hm', {})

        set_method(hm_name, openstack_mappings.hm_type(c, hm['type']),
                   hm['delay'], hm['timeout'], hm['max_retries'],
                   method=method, url=url, expect_code=expect_code,
                   axapi_args=args)

    def create(self, context, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10WriteHMStatusContext(self, context, h, action='create') as c:
            try:
                self._set(c, c.client.slb.hm.create, context, hm)
            except acos_errors.Exists:
                pass

            if pool_id is not None:
                c.client.slb.service_group.update(
                    self._pool_name(context, pool_id),
                    health_monitor=self._meta_name(hm))

            for pool in hm['pools']:
                if pool['pool_id'] == pool_id:
                    continue
                c.client.slb.service_group.update(
                    self._pool_name(context, pool['pool_id']),
                    health_monitor=self._meta_name(hm))

    def update(self, context, old_hm, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10WriteHMStatusContext(self, context, h) as c:
            self._set(c, c.client.slb.hm.update, context, hm)

    def _dissociate(self, c, context, hm, pool_id):
        """Remove a pool association"""
        pool_name = self._pool_name(context, pool_id)
        c.client.slb.service_group.update(pool_name, health_monitor="",
                                          health_check_disable=True)

    def dissociate(self, c, context, hm, pool_id):
        """Remove a pool association, and the healthmonitor if its the last one"""

        self._dissociate(c, context, hm, pool_id)
        pools = hm.get("pools", [])
        if not any(p for p in pools if p.get("pool_id") != pool_id):
            self._delete_unused(c, context, hm)

    def _delete(self, c, context, hm):
        """Delete a healthmonitor and ALL its pool associations"""
        pools = hm.get("pools", [])

        for pool in pools:
            pool_id = pool.get("pool_id")
            self._dissociate(c, context, hm, pool_id)

        self._delete_unused(c, context, hm)

    def _delete_unused(self, c, context, hm):
        try:
            c.client.slb.hm.delete(self._meta_name(hm))
        except acos_errors.InUse:
            LOG.error("Cannot delete a health monitor with existing associations")
            raise
        except acos_errors.NotFound:
            pass

    def delete(self, context, hm, pool_id):
        h = hm.copy()
        # Get the binding count to see if we need to perform disassociation

        h['pool_id'] = pool_id
        with a10.A10DeleteHMContext(self, context, h) as c:

            if pool_id is None:
                # Delete the whole healthmonitor
                self._delete(c, context, hm)
            else:
                # Disassociate this pool
                self.dissociate(c, context, hm, pool_id)
