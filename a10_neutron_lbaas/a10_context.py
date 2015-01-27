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

import logging

import acos_client.errors as acos_errors

LOG = logging.getLogger(__name__)


class A10Context(object):

    def __init__(self, handler, openstack_context, openstack_lbaas_obj,
                 **kwargs):
        self.handler = handler
        self.openstack_driver = handler.openstack_driver
        self.a10_driver = handler.a10_driver
        self.hooks = self.a10_driver.hooks
        self.openstack_context = openstack_context
        self.openstack_lbaas_obj = openstack_lbaas_obj
        self.device_name = kwargs.get('device_name', None)
        LOG.debug("A10Context obj=%s", openstack_lbaas_obj)

    def __enter__(self):
        self.get_tenant_id()
        if self.device_name:
            d = self.a10_driver.config.devices[self.device_name]
        else:
            d = self.a10_driver._select_a10_device(self.tenant_id)
        self.device_cfg = d
        self.client = self.a10_driver._get_a10_client(self.device_cfg)
        self.select_appliance_partition()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.client.session.close()
        except acos_errors.InvalidSessionID:
            pass

        if exc_type is not None:
            return False

    def get_tenant_id(self):
        if hasattr(self.openstack_lbaas_obj, 'tenant_id'):
            self.tenant_id = self.openstack_lbaas_obj.tenant_id
        else:
            self.tenant_id = self.openstack_lbaas_obj['tenant_id']

    def select_appliance_partition(self):
        # If we are not using appliance partitions, we are done.
        if self.device_cfg['v_method'].lower() != 'adp':
            return

        # Try to make the requested partition active
        name = self.tenant_id[0:13]
        try:
            self.client.system.partition.active(name)
            return
        except acos_errors.NotFound:
            pass

        # Create it if not found
        self.hooks.partition_create(self.client, self.openstack_context, name)
        self.client.system.partition.active(name)


class A10WriteContext(A10Context):

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            try:
                self.client.system.action.write_memory()
            except acos_errors.InvalidSessionID:
                pass

            for v in self.device_cfg.get('ha_sync_list', []):
                self.client.ha.sync(v['ip'], v['username'], v['password'])

        super(A10WriteContext, self).__exit__(exc_type, exc_value, traceback)


# class A10WriteStatusContext(A10WriteContext):

#     def __exit__(self, exc_type, exc_value, traceback):
#         if exc_type is None:
#             self.openstack_manager.active(self.openstack_context,
#                                           self.openstack_lbaas_obj.id)
#         else:
#             self.openstack_manager.failed(self.openstack_context,
#                                           self.openstack_lbaas_obj.id)

#         super(A10WriteStatusContext, self).__exit__(exc_type, exc_value,
#                                                     traceback)


class A10DeleteContextBase(A10WriteContext):

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # self.openstack_manager.db_delete(self.openstack_context,
            #                                  self.openstack_lbaas_obj.id)
            self.partition_cleanup_check()

        super(A10DeleteContextBase, self).__exit__(exc_type, exc_value,
                                                   traceback)

    def remaining_root_objects(self):
        return 1

    def partition_cleanup_check(self):
        # If we are not using appliance partitions, we are done.
        if self.device_cfg['v_method'].lower() != 'adp':
            return

        n = self.remaining_root_objects()
        if n == 0:
            try:
                name = self.tenant_id[0:13]
                self.hooks.partition_delete(self.client, self.openstack_context, name)
            except Exception:
                LOG.exception("A10Driver: partition cleanup failed; ignoring")
