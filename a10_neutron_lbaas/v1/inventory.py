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

import a10_neutron_lbaas.inventory as inventory


class InventoryV1(inventory.InventoryBase):
    pass
    # def root_vip_id(self, openstack_context, openstack_lbaas_obj):
    #     """Returns the vip_id the passed object is part of"""
    #     pass

    # def find(self, openstack_lbaas_obj):
    #     vip_id = self.root_vip_id(openstack_lbaas_obj)
    #     slb = a10_context.db_operations.get_slb_v1(vip_id)
    #     if slb is None:
    #         # Assign this vip to an appliance
    #         appliance = a10_context.select_appliance()
    #         slb = models.default(
    #             models.A10SLBV1,
    #             vip_id=vip_id,
    #             a10_appliance=appliance)
    #         a10_context.db_operations.add(slb)

    #     return slb
