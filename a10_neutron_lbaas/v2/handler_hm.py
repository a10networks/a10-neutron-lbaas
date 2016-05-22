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
import handler_base_v2
import logging
import v2_context as a10

from a10_neutron_lbaas.acos import openstack_mappings

LOG = logging.getLogger(__name__)


class HealthMonitorHandler(handler_base_v2.HandlerBaseV2):

    def _name(self, hm):
        return hm.id[0:28]

    def _set(self, c, set_method, context, hm):
        hm_name = self._meta_name(hm)
        method = None
        url = None
        expect_code = None
        if hm.type in ['HTTP', 'HTTPS']:
            method = hm.http_method
            url = hm.url_path
            expect_code = hm.expected_codes

        self._ensure_timeout_does_not_exceed_delay(hm)

        args = self.meta(hm, 'hm', {})

        set_method(hm_name, openstack_mappings.hm_type(c, hm.type),
                   hm.delay, hm.timeout, hm.max_retries,
                   method=method, url=url, expect_code=expect_code,
                   axapi_args=args)

    def _ensure_timeout_does_not_exceed_delay(self, hm):
        if hm.delay < hm.timeout and hm.timeout > 0:
            hm.delay = hm.timeout

    def _disable_health_monitor(self, c, context, hm):
        c.client.slb.service_group.update(
            self._pool_name(context, pool=hm.pool),
            health_monitor="", health_check_disable=True)

    def _create(self, c, context, hm):
        try:
            self._set(c, c.client.slb.hm.create, context, hm)
        except acos_errors.Exists:
            pass

        # Disable any potentially existing health monitor.
        c.client.slb.service_group.update(
            self._pool_name(context, pool=hm.pool),
            health_monitor="", health_check_disable=True)

        c.client.slb.service_group.update(
            self._pool_name(context, pool=hm.pool),
            health_monitor=self._meta_name(hm), health_check_disable=False)

    def create(self, context, hm):
        LOG.debug("HealthMonitorHandler.create(): hm=%s, context=%s" % (dir(hm), context))
        with a10.A10WriteStatusContext(self, context, hm) as c:
            self._create(c, context, hm)

    def update(self, context, old_hm, hm):
        with a10.A10WriteStatusContext(self, context, hm) as c:
            if old_hm.pool and not hm.pool:
                pool_name = self._pool_name(context, pool=old_hm.pool)
                c.client.slb.service_group.update(pool_name,
                                                  health_monitor="",
                                                  health_check_disable=True)
            elif old_hm.pool != hm.pool:
                pool_name = self._pool_name(context, pool=hm.pool)

                # Remove any existing association.  This should be moved into a method.
                c.client.slb.service_group.update(pool_name,
                                                  health_monitor="",
                                                  health_check_disable=True)
                c.client.slb.service_group.update(pool_name,
                                                  health_monitor=self._meta_name(hm),
                                                  health_check_disable=False)
            self._set(c, c.client.slb.hm.update, context, hm)

    def _delete(self, c, context, hm):
        LOG.debug("HealthMonitorHandler.delete(): hm=%s, context=%s" % (hm, context))
        pool_name = self._pool_name(context, pool=hm.pool)
        LOG.debug("HealthMonitorHandler.delete(): Updating Pool %s" % (pool_name))
        c.client.slb.service_group.update(pool_name, health_monitor="",
                                          health_check_disable=True)
        c.client.slb.hm.delete(self._meta_name(hm))

    def delete(self, context, hm):
        with a10.A10DeleteContext(self, context, hm) as c:
            self._delete(c, context, hm)
