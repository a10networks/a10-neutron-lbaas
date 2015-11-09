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


class InventoryV1(inventory.InventoryBase):

    def find(self, openstack_lbaas_obj):
        # Puts all of a tenant's v1 objects on the same appliance
        tenant_id = self.a10_context.tenant_id
        tenant = self.db_operations.get_tenant_appliance(tenant_id)
        if tenant is None:
            # Assign this tenant to an appliance
            appliance = self.select_appliance()
            tenant = models.default(
                models.A10TenantAppliance,
                tenant_id=tenant_id,
                a10_appliance=appliance)
            self.db_operations.add(tenant)

        return tenant.a10_appliance
