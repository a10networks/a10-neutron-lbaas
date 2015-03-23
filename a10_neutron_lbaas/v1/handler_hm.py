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

import a10_neutron_lbaas.a10_openstack_map as a10_os
import handler_base_v1
import v1_context as a10


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

        set_method(hm_name, a10_os.hm_type(c, hm['type']),
                   hm['delay'], hm['timeout'], hm['max_retries'],
                   method=method, url=url, expect_code=expect_code,
                   axapi_args=args)

    def create(self, context, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10WriteHMStatusContext(self, context, h) as c:
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

    def _delete(self, c, context, hm):
        c.client.slb.hm.delete(self._meta_name(hm))

    def delete(self, context, hm, pool_id):
        h = hm.copy()
        h['pool_id'] = pool_id
        with a10.A10DeleteHMContext(self, context, h) as c:
            if self.neutron.hm_binding_count(context, hm['id']) <= 1:
                try:
                    self._delete(c, context, hm)
                except acos_errors.InUse:
                    pass

            pool_name = self._pool_name(context, pool_id)
            c.client.slb.service_group.update(pool_name, health_monitor="")
