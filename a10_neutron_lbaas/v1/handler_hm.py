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

import handler_base
import v1_context as a10


class HealthMonitorHandler(handler_base.HandlerBase):

    def _hm_name(self, hm):
        return hm['id'][0:28]

    def _hm_binding_count(self, context, hm_id):
        return self.openstack_driver._hm_binding_count(context, hm_id)

    def _set(self, c, set_method, context, hm):
        hm_map = {
            'PING': c.client.slb.hm.ICMP,
            'TCP': c.client.slb.hm.TCP,
            'HTTP': c.client.slb.hm.HTTP,
            'HTTPS': c.client.slb.hm.HTTPS
        }

        hm_name = self._hm_name(hm)
        method = None
        url = None
        expect_code = None
        if hm['type'] in ['HTTP', 'HTTPS']:
            method = hm['http_method']
            url = hm['url_path']
            expect_code = hm['expected_codes']

        set_method(hm_name, hm_map[hm['type']],
                   hm['delay'], hm['timeout'], hm['max_retries'],
                   method=method, url=url, expect_code=expect_code)

    def create(self, context, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10WriteHMStatusContext(self, context, h) as c:
            self._set(c, c.client.slb.hm.create, context, hm)

            if pool_id is not None:
                c.client.slb.service_group.update(
                    pool_id,
                    health_monitor=self._hm_name(hm))

            for pool in hm['pools']:
                if pool['pool_id'] == pool_id:
                    continue
                c.client.slb.service_group.update(
                    pool['pool_id'],
                    health_monitor=self._hm_name(hm))

    def update(self, context, old_hm, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10WriteHMStatusContext(self, context, h) as c:
            self._set(c, c.client.slb.hm.update, context, hm)

    def _delete(self, c, context, hm):
        c.client.slb.hm.delete(self._hm_name(hm))

    def delete(self, context, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10DeleteHMContext(self, context, h) as c:
            if self._hm_binding_count(context, hm['id']) <= 1:
                self._delete(c, context, hm)

            c.client.slb.service_group.update(pool_id, health_monitor="")
