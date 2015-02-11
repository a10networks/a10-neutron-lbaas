# Copyright 2014, A10 Networks
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


class PlumbingHooks(object):

    def __init__(self, driver):
        self.driver = driver
        self.appliance_hash = acos_client.Hash(self.driver.config.devices.keys())

    def select_device(self, tenant_id):
        # Must return device dict from config.py
        s = self.appliance_hash.get_server(tenant_id)
        return self.driver.config.devices[s]

    def partition_create(self, client, context, partition_name):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, context, partition_name):
        client.system.partition.delete(partition_name)

    def after_member_create(self, client, context, member):
        pass

    def after_member_update(self, client, context, member):
        pass

    def after_member_delete(self, client, context, member):
        pass

    def after_vip_create(self, client, context, vip):
        pass

    def after_vip_update(self, client, context, vip):
        pass

    def after_vip_delete(self, client, context, vip):
        pass
