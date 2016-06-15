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

from a10_neutron_lbaas.v2 import handler_base_v2
from a10_neutron_lbaas.v2 import handler_hm
from a10_neutron_lbaas.v2 import handler_lb
from a10_neutron_lbaas.v2 import handler_listener
from a10_neutron_lbaas.v2 import handler_member
from a10_neutron_lbaas.v2 import handler_pool

import logging

LOG = logging.getLogger(__name__)


class LoadBalancerQueuedV2(handler_base_v2.HandlerBaseV2):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        super(LoadBalancerQueuedV2, self).__init__(a10_driver, 
                                                   openstack_driver, 
                                                   neutron=neutron)
        self.lb_h = handler_lb.LoadbalancerHandler(a10_driver,
                                                   openstack_driver.load_balancer,
                                                   neutron=neutron)
        self.worker = worker
        self.neutron = neutron

    def create(self, context, lb):
        self.worker.add_to_queue([self.lb_h.create, context, lb])

    def update(self, context, old_lb, lb):
        self.worker.add_to_queue([self.lb_h.update, context, old_lb, lb])

    def delete(self, context, lb):
        self.worker.add_to_queue([self.lb_h.delete, context, lb])

    def refresh(self, context, lb):
        self.worker.add_to_queue([self.lb_h.refresh, context, lb])

    def stats(self, context, lb):
        self.worker.add_to_queue([self.lb_h.stats, context, lb])

    def _name(self, lb):
        self.worker.add_to_queue([self.lb_h._name, lb])

class ListenerQueuedV2(handler_base_v2.HandlerBaseV2):

    def __init__(self, worker, a10_driver, openstack_driver, neutron, barbican_client):
        super(ListenerQueuedV2, self).__init__(a10_driver, 
                                               openstack_driver, 
                                               neutron=neutron)
        self.listener_h = handler_listener.ListenerHandler(a10_driver,
                                                           openstack_driver.listener,
                                                           neutron=neutron,
                                                           barbican_client=barbican_client)
        self.worker = worker
        self.neutron = neutron

    def create(self, context, listener):
        self.worker.add_to_queue([self.listener_h.create, context, listener])

    def update(self, context, old_listener, listener):
        self.worker.add_to_queue([self.listener_h.update, context, old_listener, listener])

    def delete(self, context, listener):
        self.worker.add_to_queue([self.listener_h.delete, context, listener])

    def _update(self, c, context, listener):
        self.worker.add_to_queue([self.listener_h._update, c, context, listener])

class PoolQueuedV2(handler_base_v2.HandlerBaseV2):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        super(PoolQueuedV2, self).__init__(a10_driver, 
                                           openstack_driver, 
                                           neutron=neutron)
        self.pool_h = handler_pool.PoolHandler(a10_driver,
                                               openstack_driver.pool,
                                               neutron=neutron)
        self.worker = worker
        self.neutron = neutron

    def create(self, context, pool):
        self.worker.add_to_queue([self.pool_h.create, context, pool])

    def update(self, context, old_pool, pool):
        self.worker.add_to_queue([self.pool_h.update, context, old_pool, pool])

    def delete(self, context, pool):
        self.worker.add_to_queue([self.pool_h.delete, context, pool])

    def stats(self, context, pool):
        self.worker.add_to_queue([self.pool_h.stats, context, pool])

class MemberQueuedV2(handler_base_v2.HandlerBaseV2):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        super(MemberQueuedV2, self).__init__(a10_driver, 
                                             openstack_driver, 
                                             neutron=neutron)
        self.member_h = handler_member.MemberHandler(a10_driver,
                                                     openstack_driver.member,
                                                     neutron=neutron)
        self.worker = worker
        self.neutron = neutron

    def create(self, context, member):
        self.worker.add_to_queue([self.member_h.create, context, member])

    def update(self, context, old_member, member):
        self.worker.add_to_queue([self.member_h.update, context, old_member, member])

    def delete(self, context, member):
        self.worker.add_to_queue([self.member_h.delete, context, member])

    def _get_name(self, member, ip):
        self.worker.add_to_queue([self.member_h._get_name, member, ip])

class HealthMonitorQueuedV2(handler_base_v2.HandlerBaseV2):

    def __init__(self, worker, a10_driver, openstack_driver, neutron):
        super(HealthMonitorQueuedV2, self).__init__(a10_driver, 
                                                    openstack_driver, 
                                                    neutron=neutron)
        self.hm_h = handler_hm.HealthMonitorHandler(a10_driver,
                                                    openstack_driver.health_monitor,
                                                    neutron=neutron)
        self.worker = worker
        self.neutron = neutron

    def create(self, context, hm):
        self.worker.add_to_queue([self.hm_h.create, context, hm])

    def update(self, context, old_hm, hm):
        self.worker.add_to_queue([self.hm_h.update, context, old_hm, hm])

    def delete(self, context, hm):
        self.worker.add_to_queue([self.hm_h.delete, context, hm])

    def dissociate(self, c, context, hm, pool_id):
        self.worker.add_to_queue([self.hm_h.dissociate, c, context, hm, pool_id])
