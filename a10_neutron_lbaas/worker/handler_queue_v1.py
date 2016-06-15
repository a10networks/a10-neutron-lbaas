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

from a10_neutron_lbaas.v1 import handler_base_v1
from a10_neutron_lbaas.v1 import handler_hm
from a10_neutron_lbaas.v1 import handler_member
from a10_neutron_lbaas.v1 import handler_pool
from a10_neutron_lbaas.v1 import handler_vip

import logging

LOG = logging.getLogger(__name__)


class VipQueuedV1(handler_base_v1.HandlerBaseV1):

    def __init__(self, worker, a10_driver, openstack_driver):
        super(VipQueuedV1, self).__init__(a10_driver)
        self.vip_h = handler_vip.VipHandler(a10_driver)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver

    def create(self, context, vip):
        self.worker.add_to_queue([self.vip_h.create, context, vip])

    def update(self, context, old_vip, vip):
        self.worker.add_to_queue([self.vip_h.update, context, old_vip, vip])

    def delete(self, context, vip):
        self.worker.add_to_queue([self.vip_h.delete, context, vip])


class PoolQueuedV1(handler_base_v1.HandlerBaseV1):

    def __init__(self, worker, a10_driver, openstack_driver):
        super(PoolQueuedV1, self).__init__(a10_driver)
        self.pool_h = handler_pool.PoolHandler(a10_driver)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver

    def create(self, context, pool):
        self.worker.add_to_queue([self.pool_h.create, context, pool])

    def update(self, context, old_pool, pool):
        self.worker.add_to_queue([self.pool_h.update, context, old_pool, pool])

    def delete(self, context, pool):
        self.worker.add_to_queue([self.pool_h.delete, context, pool])

    def stats(self, context, pool):
        self.worker.add_to_queue([self.pool_h.stats, context, pool])

class MemberQueuedV1(handler_base_v1.HandlerBaseV1):
    
    def __init__(self, worker, a10_driver, openstack_driver):
        super(MemberQueuedV1, self).__init__(a10_driver)
        self.member_h = handler_member.MemberHandler(a10_driver)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver

    def create(self, context, member):
        self.worker.add_to_queue([self.member_h.create, context, member])

    def update(self, context, old_member, member):
        self.worker.add_to_queue([self.member_h.update, context, old_member, member])

    def delete(self, context, member):
        self.worker.add_to_queue([self.member_h.delete, context, member])

    def _delete(self, c, context, member):
        self.worker.add_to_queue([self.member_h._delete, c, context, member])

    def _get_name(self, member, ip):
        self.worker.add_to_queue([self.member_h._get_name, member, ip])

class HealthMonitorQueuedV1(handler_base_v1.HandlerBaseV1):

    def __init__(self, worker, a10_driver, openstack_driver):
        super(HealthMonitorQueuedV1, self).__init__(a10_driver)
        self.hm_h = handler_hm.HealthMonitorHandler(a10_driver)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver

    def create(self, context, hm, pool_id):
        self.worker.add_to_queue([self.hm_h.create, context, hm, pool_id])

    def update(self, context, old_hm, hm, pool_id):
        self.worker.add_to_queue([self.hm_h.update, context, old_hm, hm, pool_id])

    def delete(self, context, hm, pool_id):
        self.worker.add_to_queue([self.hm_h.delete, context, hm, pool_id])

    def dissociate(self, c, context, hm, pool_id):
        self.worker.add_to_queue([self.hm_h.dissociate, c, context, hm, pool_id])
