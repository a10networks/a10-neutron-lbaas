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
import v2_context as a10


class HealthMonitorHandler(handler_base.HandlerBase):

    def _hm_name(self, hm):
        return hm.id[0:28]

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
        if hm.type in ['HTTP', 'HTTPS']:
            method = hm.http_method
            url = hm.url_path
            expect_code = hm.expected_codes

        set_method(hm_name, hm_map[hm.type],
                   hm.delay, hm.timeout, hm.max_retries,
                   method=method, url=url, expect_code=expect_code)

    def _create(self, c, context, hm):
        self._set(c, c.client.slb.hm.create, context, hm)

        if hm.pool:
            c.client.slb.service_group.update(
                hm.pool.id,
                health_monitor=self._hm_name(hm))

    def create(self, context, hm):
        with a10.A10WriteStatusContext(self, context, hm) as c:
            self._create(c, context, hm)

    def update(self, context, old_hm, hm):
        with a10.A10WriteStatusContext(self, context, hm) as c:
            self._set(c, c.client.slb.hm.update, context, hm)

            if hm.pool and hm.pool != old_hm.pool:
                c.client.slb.service_group.update(
                    hm.pool.id,
                    health_monitor=self._hm_name(hm))
            elif not hm.pool and old_hm.pool:
                c.client.slb.service_group.update(
                    old_hm.pool.id,
                    health_monitor='')

    def _delete(self, c, context, hm):
        c.client.slb.hm.delete(hm.id[0:28])

    def delete(self, context, hm):
        with a10.A10DeleteContext(self, context, hm) as c:
            if hm.pool:
                c.client.slb.service_group.update(hm.pool.id,
                                                  health_monitor="")
            self._delete(c, context, hm)
