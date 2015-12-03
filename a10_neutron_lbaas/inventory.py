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
import a10_neutron_lbaas.scheduling_hooks as scheduling_hooks


class InventoryBase(object):
    def __init__(self, a10_context):
        self.a10_context = a10_context
        self.a10_driver = self.a10_context.a10_driver
        self.db_operations = self.a10_context.db_operations

    def get_appliances(self):
        """Get appliances available to this tenant"""
        # Populate all the config devices
        for device_key in self.a10_driver.config.devices:
            self.db_operations.summon_appliance_configured(device_key)

        return self.db_operations.get_shared_appliances(self.a10_context.tenant_id)

    def device_appliance(self, device):
        appliance = device.get('appliance')

        if appliance is None:
            # TODO(aritrary config): Support for arbitrary options
            appliance = models.default(
                models.A10ApplianceDB,
                name=device.get('name', None),
                description=device.get('description', None),
                tenant_id=self.a10_context.tenant_id,
                host=device['host'],
                api_version=device.get('api_version', '2.1'),
                username=device['username'],
                password=device['password'])
            self.db_operations.add(appliance)

        return appliance

    def select_appliance(self, openstack_lbaas_obj, scheduling_hooks=None):
        """Chooses an appliance for a new loadbalancer

        Delegates the choice to scheduling hooks.
        """
        scheduling_hooks = scheduling_hooks or self.a10_driver.scheduling_hooks

        appliances = self.get_appliances()
        device_configs = [a.device(self.a10_context) for a in appliances]

        selected_devices = scheduling_hooks.select_devices(self.a10_context, device_configs)
        selected_device = next(selected_devices.__iter__())

        appliance = self.device_appliance(selected_device)

        return appliance

    def find(self, openstack_lbaas_obj):
        """Find or select the appliance the openstack_lbaas_obj lives on"""

        # The default, safe implementation puts all of a tenant's objects on the same appliance
        per_tenant_scheduler = scheduling_hooks.DevicePerTenant(self.a10_driver.scheduling_hooks)
        return self.select_appliance(openstack_lbaas_obj, per_tenant_scheduler)
