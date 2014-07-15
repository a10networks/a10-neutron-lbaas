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

import acos_client
import logging

import a10_config
import mgr_hm
import mgr_lb
import mgr_listener
import mgr_member
import mgr_pool

LOG = logging.getLogger(__name__)


class LbaasManager(object):

    def __init__(self, openstack_driver):
        self.openstack_driver = openstack_driver
        self.config = a10_config.A10Config()
        self.appliance_hash = acos_client.Hash(self.config.devices.keys())
        if self.config.get('verify_appliances', True):
            self._verify_appliances()

    def _select_a10_device(self, tenant_id):
        s = self.appliance_hash.get_server(tenant_id)
        return self.config.devices[s]

    def _get_a10_client(self, device_info):
        d = device_info
        protocol = d.get('protocol', 'https')
        port = {'http': 80, 'https': 443}[protocol]
        if 'port' in d:
            port = d['port']

        return acos_client.Client(d['host'],
                                  d.get('api_version', acos_client.AXAPI_21),
                                  d['username'], d['password'],
                                  port=port, protocol=protocol)

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

    @property
    def lb(self):
        return mgr_lb.LoadBalancer(self, self.openstack_driver.load_balancer)

    @property
    def listener(self):
        return mgr_listener.Listener(self, self.openstack_driver.listener)

    @property
    def pool(self):
        return mgr_pool.Pool(self, self.openstack_driver.pool)

    @property
    def member(self):
        return mgr_member.Member(self, self.openstack_driver.member)

    @property
    def hm(self):
        return mgr_hm.HealthMonitor(self, self.openstack_driver.health_monitor)
