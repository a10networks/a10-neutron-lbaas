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

from a10_neutron_lbaas import a10_exceptions as ex


class BasePlumbingHooks(object):

    def __init__(self, driver, **kwargs):
        self.driver = driver
        self.client_wrapper_class = None

    # While you can override select_device in hooks to get custom selection
    # behavior, it is much easier to use the 'device_scheduling_filters'
    # mechanism, as documented in the config file.

    def select_device(self, tenant_id, **kwargs):
        # Not a terribly useful scheduler
        raise ex.NotImplemented()

    # Newer scheduling interface, which is called in favor the one above,
    # if present.

    # def select_device_with_lbaas_obj(self, tenant_id, a10_context, lbaas_obj,
    #                                  db_session=None, **kwargs):
    #     raise ex.NotImplemented()

    def get_a10_client(self, device_info, **kwargs):
        return acos_client.Client(
            device_info['host'], device_info['api_version'],
            device_info['username'], device_info['password'],
            port=device_info['port'], protocol=device_info['protocol'])

    # Network plumbing hooks from here on out

    def partition_create(self, client, os_context, partition_name):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, os_context, partition_name):
        client.system.partition.delete(partition_name)

    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def after_member_delete(self, a10_context, os_context, member):
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        pass

    def after_vip_update(self, a10_context, os_context, vip):
        pass

    def after_vip_delete(self, a10_context, os_context, vip):
        pass

    def a10_context_exit_final(self, a10_context):
        pass

    def after_select_partition(self, a10_context):
        pass
