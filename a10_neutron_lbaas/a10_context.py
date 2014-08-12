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

    def __init__(self, handler, openstack_context, openstack_lbaas_obj):
        self.handler = handler
        self.openstack_driver = handler.openstack_driver
        self.a10_driver = handler.a10_driver
        self.openstack_context = openstack_context
        self.openstack_lbaas_obj = openstack_lbaas_obj

    def __enter__(self):
        self.get_tenant_id()
        self.device_cfg = self.a10_driver._select_a10_device(self.tenant_id)
        self.client = self.a10_driver._get_a10_client(self.device_cfg)
        self.select_appliance_partition()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.session.close()

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
        try:
            self.client.system.partition.active(self.tenant_id)
            return
        except acos_errors.NotFound:
            pass

        # Create it if not found
        self.client.system.partition.create(self.tenant_id)
        self.client.system.partition.active(self.tenant_id)


class A10WriteContext(A10Context):

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.client.system.action.write_memory()

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
                self.client.system.partition.delete(self.tenant_id)
            except Exception:
                LOG.error("A10Driver: partition cleanup failed; ignoring")
