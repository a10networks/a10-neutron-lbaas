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

import a10_neutron_lbaas.a10_context as a10_context


class A10Context(a10_context.A10Context):
    pass


class A10WriteContext(a10_context.A10WriteContext):
    pass


class A10WriteStatusContext(a10_context.A10WriteContext):

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.handler.openstack_manager.successful_completion(
                self.openstack_context,
                self.openstack_lbaas_obj)
        else:
            self.handler.openstack_manager.failed_completion(
                self.openstack_context,
                self.openstack_lbaas_obj)

        super(A10WriteStatusContext, self).__exit__(exc_type, exc_value,
                                                    traceback)


class A10DeleteContext(a10_context.A10DeleteContextBase):

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.handler.openstack_manager.successful_completion(
                self.openstack_context,
                self.openstack_lbaas_obj,
                delete=True)

        super(A10DeleteContext, self).__exit__(exc_type, exc_value, traceback)

    def remaining_root_objects(self):
        ctx = self.openstack_context
        return self.handler.neutron.loadbalancer_total(ctx, self.tenant_id)
