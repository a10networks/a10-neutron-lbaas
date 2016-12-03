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
import threading
from threading import Thread

import acos_client.errors as acos_errors

import handler_base_v2
import v2_context as a10

LOG = logging.getLogger(__name__)


class LoadbalancerHandler(handler_base_v2.HandlerBaseV2):

    def _set(self, set_method, c, context, lb):
        status = c.client.slb.UP
        if not lb.admin_state_up:
            status = c.client.slb.DOWN

        try:
            vip_meta = self.meta(lb, 'virtual_server', {})

            set_method(
                self._meta_name(lb),
                lb.vip_address,
                status,
                vrid=c.device_cfg.get('default_virtual_server_vrid'),
                axapi_body=vip_meta)
        except acos_errors.Exists:
            pass

    def _create(self, c, context, lb):
        self._set(c.client.slb.virtual_server.create, c, context, lb)

    def _stats(self, **kwargs):
        for k,v in kwargs.items():
            self.lock.acquire()

            if self.stats.get(k):
                self.stats[k] += v
            else:
                self.stats[k] = v

            self.lock.release()

    def create(self, context, lb):
        with a10.A10WriteStatusContext(self, context, lb, action='create') as c:
            self._create(c, context, lb)
            self.hooks.after_vip_create(c, context, lb)

    def update(self, context, old_lb, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._set(c.client.slb.virtual_server.update, c, context, lb)
            self.hooks.after_vip_update(c, context, lb)

    def _delete(self, c, context, lb):
        try:
            c.client.slb.virtual_server.delete(self._meta_name(lb))
        except acos_errors.NotFound:
            pass

    def delete(self, context, lb):
        with a10.A10DeleteContext(self, context, lb) as c:
            self._delete(c, context, lb)
            self.hooks.after_vip_delete(c, context, lb)

    def stats(self, context, lb):
        with a10.A10Context(self, context, lb) as c:
            name = self.meta(lb, 'id', lb.id)
            resp = c.client.slb.virtual_server.stats(name)
            
            if not resp:
                return {
                    "bytes_in": 0,
                    "bytes_out": 0,
                    "active_connections": 0,
                    "total_connections": 0,
                    "extended_stats": {}
                }

            self.stats = {}
            self.lock = threading.Lock()

            for ports in resp['stats']:
                t = Thread(target=_stats, kwargs=ports)
                t.start()

            # (TODO: Hunter) Add stats gathering for child objects

            return {
                "bytes_in": self.stats['total_fwd_bytes'],
                "bytes_out": self.stats['total_rev_bytes'],
                "active_connections": self.stats['cur_conn'],
                "total_connections": self.stats['total_conn'],
                }

    def refresh(self, context, lb):
        LOG.debug("LB Refresh called.")
        # Ensure all elements associated with this LB exist on the device.
