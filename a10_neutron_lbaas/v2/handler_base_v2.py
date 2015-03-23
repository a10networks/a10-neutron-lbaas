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

import a10_neutron_lbaas.handler_base as base
import neutron_ops


class HandlerBaseV2(base.HandlerBase):

    def __init__(self, a10_driver, openstack_manager, neutron=None):
        super(HandlerBaseV2, self).__init__(a10_driver)
        self.openstack_manager = openstack_manager
        if neutron:
            self.neutron = neutron
        else:
            self.neutron = neutron_ops.NeutronOpsV2(self)
