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


class InventoryBase(object):
    def __init__(self, a10_context):
        self.a10_context = a10_context
        self.a10_driver = self.a10_context.a10_driver
        self.db_operations = self.a10_context.db_operations

    def select_appliance(self):
        """Chooses an appliance for a new loadbalancer"""
        device = self.a10_driver._select_a10_device(self.a10_context.tenant_id)
        appliance = self.db_operations.summon_appliance_configured(device['key'])
        return appliance

    def find(self, obenstack_lbaas_ojb):
        """Find or select the appliance the openstack_lbaas_obj lives on"""
        return self.select_appliance()
