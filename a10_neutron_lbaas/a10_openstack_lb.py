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

import a10_config
import acos_client
import plumbing_hooks as hooks
import v1.handler_hm
import v1.handler_member
import v1.handler_pool
import v1.handler_vip
import v2.handler_hm
import v2.handler_lb
import v2.handler_listener
import v2.handler_member
import v2.handler_pool
import version

LOG = logging.getLogger(__name__)


class A10OpenstackLBBase(object):

    def __init__(self, openstack_driver,
                 plumbing_hooks_class=hooks.PlumbingHooks,
                 neutron_hooks_module=None):
        self.openstack_driver = openstack_driver
        self.config = a10_config.A10Config()
        self.neutron = neutron_hooks_module

        LOG.info("A10-neutron-lbaas: initializing, version=%s, acos_client=%s",
                 version.VERSION, acos_client.VERSION)

        if self.config.verify_appliances:
            self._verify_appliances()

        self.hooks = plumbing_hooks_class(self)

    def _select_a10_device(self, tenant_id):
        return self.hooks.select_device(tenant_id)

    def _get_a10_client(self, device_info):
        d = device_info
        return acos_client.Client(d['host'],
                                  d.get('api_version', acos_client.AXAPI_21),
                                  d['username'], d['password'],
                                  port=d['port'], protocol=d['protocol'])

    def _verify_appliances(self):
        LOG.info("A10Driver: verifying appliances")

        if len(self.config.devices) == 0:
            LOG.error("A10Driver: no configured appliances")

        for k, v in self.config.devices.items():
            try:
                LOG.info("A10Driver: appliance(%s) = %s", k,
                         self._get_a10_client(v).system.information())
            except Exception:
                LOG.error("A10Driver: unable to connect to configured"
                          "appliance, name=%s", k)


class A10OpenstackLBV2(A10OpenstackLBBase):

    @property
    def lb(self):
        return v2.handler_lb.LoadbalancerHandler(
            self,
            self.openstack_driver.load_balancer,
            neutron=self.neutron)

    @property
    def loadbalancer(self):
        return self.lb

    @property
    def listener(self):
        return v2.handler_listener.ListenerHandler(
            self,
            self.openstack_driver.listener,
            neutron=self.neutron)

    @property
    def pool(self):
        return v2.handler_pool.PoolHandler(
            self, self.openstack_driver.pool,
            neutron=self.neutron)

    @property
    def member(self):
        return v2.handler_member.MemberHandler(
            self,
            self.openstack_driver.member,
            neutron=self.neutron)

    @property
    def hm(self):
        return v2.handler_hm.HealthMonitorHandler(
            self,
            self.openstack_driver.health_monitor,
            neutron=self.neutron)


class A10OpenstackLBV1(A10OpenstackLBBase):

    @property
    def pool(self):
        return v1.handler_pool.PoolHandler(self)

    @property
    def vip(self):
        return v1.handler_vip.VipHandler(self)

    @property
    def member(self):
        return v1.handler_member.MemberHandler(self)

    @property
    def hm(self):
        return v1.handler_hm.HealthMonitorHandler(self)
