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


class InventoryBase(object):
    def __init__(self, a10_context):
        self.a10_context = a10_context
        self.a10_driver = self.a10_context.a10_driver
        self.db_operations = self.a10_context.db_operations

    def tenant_appliance(self):
        """Chooses the appliance a tenant is already on, or assigns it"""
        tenant_id = self.a10_context.tenant_id
        tenant = self.db_operations.get_tenant_appliance(tenant_id)
        if tenant is None:
            # Assign this tenant to an appliance
            appliance = self.select_tenant_appliance()
            tenant = models.default(
                models.A10TenantAppliance,
                tenant_id=tenant_id,
                a10_appliance=appliance)
            self.db_operations.add(tenant)

        return tenant.a10_appliance

    def select_tenant_appliance(self):
        """Chooses an appliance affinity for a new tenant"""
        device = self.a10_driver._select_a10_device(self.a10_context.tenant_id)
        appliance = self.db_operations.summon_appliance_configured(device['key'])
        return appliance

    def select_appliance(self, openstack_lbaas_obj):
        """Chooses an appliance for a new loadbalancer

        When we add scheduling hooks, this will delegate the choice to the scheduler.
        For now, it always chooses based on tenant affinity.
        """
        return self.tenant_appliance()

    def find(self, openstack_lbaas_obj):
        """Find or select the appliance the openstack_lbaas_obj lives on"""

        # The default, safe implementation puts all of a tenant's objects on the same appliance
        return self.tenant_appliance()
