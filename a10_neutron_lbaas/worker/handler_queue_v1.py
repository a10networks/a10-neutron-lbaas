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

from a10_neutron_lbaas.v1 import handler_hm
from a10_neutron_lbaas.v1 import handler_member
from a10_neutron_lbaas.v1 import handler_pool
from a10_neutron_lbaas.v1 import handler_vip

import logging

LOG = logging.getLogger(__name__)


class VipQueuedV1(object):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        self.vip_h = handler_vip.VipHandler(a10_driver,
                                            openstack_driver.vip,
                                            neutron=neutron)
        self.worker = worker
        self.openstack_driver = openstack_driver
        self.neutron = neutron
        self.openstack_manager = openstack_driver
        self.a10_driver = a10_driver

    def create(self, context, vip):
        self.worker.add_to_queue([self.vip_h.create, context, vip])

    def update(self, context, old_vip, vip):
        self.worker.add_to_queue([self.vip_h.update, context, old_vip, vip])

    def delete(self, context, vip):
        self.worker.add_to_queue([self.vip_h.delete, context, vip])


class PoolQueuedV1(object):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        self.pool_h = handler_pool.PoolHandler(a10_driver,
                                               openstack_driver.pool,
                                               neutron=neutron)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver
        self.neutron = neutron
        self.openstack_manager = openstack_driver

    def create(self, context, pool):
        self.worker.add_to_queue([self.pool_h.create, context, pool])

    def update(self, context, old_pool, pool):
        self.worker.add_to_queue([self.pool_h.update, context, old_pool, pool])

    def delete(self, context, pool):
        self.worker.add_to_queue([self.pool_h.delete, context, pool])


class MemberQueuedV1(object):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        self.pool_h = handler_member.MemberHandler(a10_driver,
                                                   openstack_driver.member,
                                                   neutron=neutron)
        self.worker = worker
        self.a10_driver = a10_driver
        self.openstack_driver = openstack_driver
        self.neutron = neutron
        self.openstack_manager = openstack_driver

    def create(self, context, member):
        self.worker.add_to_queue([self.pool_h.create, context, member])

    def update(self, context, old_member, member):
        self.worker.add_to_queue([self.pool_h.update, context, old_member, member])

    def delete(self, context, member):
        self.worker.add_to_queue([self.pool_h.delete, context, member])


class HealthMonitorQueuedV1(object):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        self.hm_h = handler_hm.HealthMonitorHandler(a10_driver,
                                                    openstack_driver.health_monitor,
                                                    neutron=neutron)
        self.worker = worker
        self.a10_driver = a10_driver
        self.neutron = neutron
        self.openstack_manager = openstack_driver
        self.openstack_driver = openstack_driver

    def create(self, context, hm):
        self.worker.add_to_queue([self.hm_h.create, context, hm])

    def update(self, context, old_hm, hm):
        self.worker.add_to_queue([self.hm_h.update, context, old_hm, hm])

    def delete(self, context, hm):
        self.worker.add_to_queue([self.hm_h.delete, context, hm])
