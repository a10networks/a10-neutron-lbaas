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

import errno
import logging
import socket
import time

from a10_neutron_lbaas import a10_common

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
            vip_args = a10_common._virtual_server(vip_meta, c.device_cfg)
            set_method(
                self._meta_name(lb),
                lb.vip_address,
                status,
                axapi_args=vip_args)
        except acos_errors.Exists:
            pass

    def _create(self, c, context, lb):
        created = self._create_spinlock(c, context, lb)
        self.hooks.after_vip_create(c, context, lb)

    def _create_spinlock(self, c, context, lb):
        sleep_time = 0.25
        lock_time = 600
        skip_errs = [errno.EHOSTUNREACH]
        running = True
        time_begin = time.time()
        
        while running:
            try:
                # import pdb; pdb.set_trace()
                self._set(c.client.slb.virtual_server.create, c, context, lb)
                running = False
                break
            except socket.error as e:
                last_e = e
                if e.errno not in skip_errs:
                    raise
            except Exception as ex:
                last_e = ex
                running = False
                break
            time_end = time.time()
            if (time_end - time_begin) >= lock_time:
                if not last_e is None:
                    LOG.exception(last_e)
                running = False
                break

    def create(self, context, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._create(c, context, lb)

    def update(self, context, old_lb, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._set(c.client.slb.virtual_server.update, c, context, lb)
            self.hooks.after_vip_update(c, context, lb)

    def _delete(self, c, context, lb):
        try:
            c.client.slb.virtual_server.delete(self._meta_name(lb))
        except acos_errors.NotFound:
            pass
        c.db_operations.delete_slb_v2(lb.id)

    def delete(self, context, lb):
        with a10.A10DeleteContext(self, context, lb) as c:
            self._delete(c, context, lb)
            self.hooks.after_vip_delete(c, context, lb)

    def stats(self, context, lb):
        pass

    def refresh(self, context, lb):
        pass
