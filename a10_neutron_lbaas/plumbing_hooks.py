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

from a10_neutron_lbaas import a10_exceptions as ex


class PlumbingHooks(object):

    def __init__(self, driver, devices=None):
        self.driver = driver
        if devices is not None:
            self.devices = devices
        elif get_device_func is not None:
            self.devices = get_devices_func()
        else:
            self.devices = self.driver.config.get_devices()

        self.scheduling_filters = map(lambda x: x(self.driver, self.devices),
                                      config.get('device_scheduling_filters'))

    # While you can override select_device in hooks to get custom selection
    # behavior, it is much easier to use the 'device_scheduling_filters'
    # mechanism, as documented in the config file.

    def select_device(self, tenant_id, a10_context=None, lbaas_obj=None):
        devices = self.devices
        for x in self.scheduling_filters:
            devices = x.select_device(devices, tenant_id, lbaas_obj)
            if len(devices) == 0:
                raise Error()
            elif len(devices) == 1:
                return devices[0]

        # If we get here, all of our filters ran and we have more than one
        # device to choose from. Just grab the first.
        log.WARNING("stuff choosing first your filters are junk")
        return devices[0]

    # Network plumbing hooks from here on out

    def partition_create(self, client, context, partition_name, a10_context=None):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, context, partition_name, a10_context=None):
        client.system.partition.delete(partition_name)

    def after_member_create(self, a10_context, context, member):
        pass

    def after_member_update(self, a10_context, context, member):
        pass

    def after_member_delete(self, a10_context, context, member):
        pass

    def after_vip_create(self, a10_context, context, vip):
        pass

    def after_vip_update(self, a10_context, context, vip):
        pass

    def after_vip_delete(self, a10_context, context, vip):
        pass


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active.

class VThunderPlumbingHooks(PlumbingHooks):

    def after_vip_create(self, a10_context, context, vip):
        instance = todo_db_query(find device_cfg['name'])

        instance_manager = instance_manager.Foo(todo)
        return self.instance_manager.plumb_instance_subnet(
            instance.nova_instance_id,
            a10_context.device_cfg.get('vip_subnet_id'],
            vip.ip_address or vip['ip_address'], ## todo, stupid separate obj models
            wrong_ips=[a10_context.device_cfg['host']])
