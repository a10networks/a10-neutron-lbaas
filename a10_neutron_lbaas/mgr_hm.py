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

import a10_context as a10


class HealthMonitorManager(ManagerBase):

    def _set(self, c, set_method, context, hm):
        hm_map = {
            'PING': c.client.slb.hm.ICMP,
            'TCP': c.client.slb.hm.TCP,
            'HTTP': c.client.slb.hm.HTTP,
            'HTTPS': c.client.slb.hm.HTTPS
        }

        hm_name = hm.id[0:28]
        set_method(hm_name, hm_map[hm.type],
                   hm.delay, hm.timeout, hm.max_retries,
                   hm.http_method, hm.url_path, hm.expected_codes)

        if hm.pool:
            c.client.slb.service_group.update(hm.pool.id,
                                              health_monitor=hm_name)

    def _create(self, c, context, hm):
        self._set(c, c.client.slb.hm.create, context, hm)

    def create(self, context, hm):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._create(c, context, hm)

    def update(self, context, old_hm, hm):
        with a10.A10WriteStatusContext(self, context, pool) as c:
            self._set(c, c.client.slb.hm.update, context, hm)

    def _delete(self, c, context, hm):
        c.client.slb.hm.delete(hm.id[0:28])

    def delete(self, context, hm):
        with a10.A10DeleteContext(self, context, pool) as c:
            if hm.pool:
                c.client.slb.service_group.update(hm.pool.id,
                                                  health_monitor="")
            self._delete(c, context, hm)
