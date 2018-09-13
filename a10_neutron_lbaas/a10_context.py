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

from a10_neutron_lbaas.vthunder import keystone as keystone_helpers

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
        self.action = kwargs.get('action', '')
        LOG.debug("A10Context obj=%s", openstack_lbaas_obj)
        LOG.debug("A10Context action=%s", self.action)
        self.partition_name = "shared"

    def _get_device(self):
        if self.device_name:
            d = self.a10_driver.config.get_device(self.device_name)
        else:
            d = self.a10_driver._select_a10_device(self.tenant_id, a10_context=self,
                                                   lbaas_obj=self.openstack_lbaas_obj,
                                                   action=self.action)
        return d

    def _get_client(self, device_cfg):
        return self.a10_driver._get_a10_client(device_cfg, action=self.action)

    def __enter__(self):
        self.get_tenant_id()
        self.device_cfg = self._get_device()
        self.client = self._get_client(self.device_cfg)
        self.get_partition_key()
        self.select_appliance_partition()
        if hasattr(self.hooks, 'after_select_partition'):
            self.hooks.after_select_partition(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.client.session.close()
        except acos_errors.InvalidSessionID:
            pass

        if hasattr(self.hooks, 'a10_context_exit_final'):
            self.hooks.a10_context_exit_final(self)

        if exc_type is not None:
            return False

    def get_tenant_id(self):
        if hasattr(self.openstack_lbaas_obj, 'tenant_id'):
            self.tenant_id = self.openstack_lbaas_obj.root_loadbalancer.tenant_id
        else:
            self.tenant_id = self.openstack_lbaas_obj['tenant_id']

    def get_partition_key(self):
        # If use_parent_project is enabled, return that. Else, typical behavior. 
        self.partition_key = self.tenant_id
        if self.a10_driver.config.get("use_parent_project") and self.openstack_context:
            # Hoping we can avoid making this call but I don't think thats possible
            keystone_context = keystone_helpers.KeystoneFromContext(self.a10_driver.config, self.openstack_context)
            thisproject = keystone_context.client.projects.get(self.tenant_id)
            if not thisproject.parent_id == thisproject.domain_id:
                self.partition_key = thisproject.parent_id

    def select_appliance_partition(self):
        self.get_partition_key()

        name = self.device_cfg.get("shared_partition", "shared")

        if self.device_cfg['v_method'].lower() == 'adp':
            name = self.partition_key[0:13]

        # If we are not using appliance partitions, we are done.
        if name == 'shared':
            return

        self.partition_name = name

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
        if exc_type is None and self.device_cfg.get('write_memory', True):
            try:
                partition_deleted = getattr(self, "partition_deleted", False)
                partition_name = None if partition_deleted else self.partition_name
                self.client.system.action.activate_and_write(partition_name)

            except acos_errors.InvalidSessionID:
                pass

            for v in self.device_cfg.get('ha_sync_list', []):
                self.client.ha.sync(v['ip'], v['username'], v['password'])

        super(A10WriteContext, self).__exit__(exc_type, exc_value, traceback)


class A10ReplayContext(A10WriteContext):

    def __init__(self, *args, **kwargs):
        self._appliance = kwargs.pop('appliance', None)
        super(A10ReplayContext, self).__init__(*args, **kwargs)

    def _get_device(self):
        return self._appliance.device(self)

    def _get_client(self, device_cfg):
        return self._appliance.client(self, device_cfg, action=self.action)


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
            self.partition_deleted = False
            self.partition_cleanup_check()

        super(A10DeleteContextBase, self).__exit__(exc_type, exc_value, traceback)

    def remaining_root_objects(self):
        return 1

    def partition_cleanup_check(self):
        # If we are not using appliance partitions, we are done.

        if self.device_cfg['v_method'].lower() != 'adp':
            return
        self.get_partition_key()
        n = self.remaining_root_objects()
        LOG.debug("A10DeleteContext.partition_cleanup_check(): n=%s" % (n))
        if n == 0 and not self.a10_driver.config.get("disable_partition_delete"):
            try:
                name = self.partition_key[0:13]
                if not name:
                    return
                self.hooks.partition_delete(self.client, self.openstack_context, name)
                # Run post-post cleanup hook if exists
                if hasattr(self.hooks, "partition_delete_last"):
                    self.hooks.partition_delete_last(self.client, self.openstack_context, name,
                                                     self.openstack_lbaas_obj)
                LOG.debug("hooks.partition_delete of %s succeeded " % (name))
                self.partition_deleted = True
            except Exception:
                LOG.exception("A10Driver: partition cleanup failed; ignoring")
