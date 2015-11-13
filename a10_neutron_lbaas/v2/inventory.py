# Copyright 2015,  A10 Networks
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
#    under the License.from neutron.db import model_base

import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.inventory as inventory


class InventoryV2(inventory.InventoryBase):

    def find(self, openstack_lbaas_obj):
        loadbalancer = openstack_lbaas_obj.root_loadbalancer
        slb = self.db_operations.get_slb_v2(loadbalancer.id)
        if slb is None:
            # Assign this loadbalancer to an appliance
            appliance = self.select_appliance()
            slb = models.default(
                models.A10SLBV2,
                lbaas_loadbalancer_id=loadbalancer.id,
                a10_appliance=appliance)
            self.db_operations.add(slb)

        return slb.a10_appliance
