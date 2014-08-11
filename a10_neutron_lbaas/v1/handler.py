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

import a10_exceptions as a10_ex
import acos_client.errors as acos_errors
import v2_context as a10


class LbaasHandlerV1(object):

    def __init__(self, a10_driver)
        self.a10_driver = a10_driver
        self.openstack_driver = self.a10_driver.openstack_driver

    def create_vip(self, context, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:

    def update_vip(self, context, old_vip, vip):
        with a10.A10WriteStatusContext(self, context, vip) as c:

    def delete_vip(self, context, vip):
        with a10.A10DeleteContext(self, context, vip) as c:

    def create_pool(self, context, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:

    def update_pool(self, context, old_pool, pool):
        with a10.A10WriteStatusContext(self, context, pool) as c:

    def delete_pool(self, context, pool):
        with a10.A10DeleteContext(self, context, pool) as c:

    def stats(self, context, pool_id):
        with a10.A10Context(self, context, lb_obj) as c:

    def create_member(self, context, member):
        with a10.A10WriteStatusContext(self, context, member) as c:

    def update_member(self, context, old_member, member):
        with a10.A10WriteStatusContext(self, context, member) as c:

    def delete_member(self, context, member):
        with a10.A10DeleteContext(self, context, member) as c:

    def update_pool_health_monitor(self, context, old_health_monitor,
                                   health_monitor, pool_id):
        with a10.A10WriteStatusContext(self, context, health_monitor) as c:

    def create_pool_health_monitor(self, context, health_monitor, pool_id):
        with a10.A10WriteStatusContext(self, context, health_monitor) as c:

    def delete_pool_health_monitor(self, context, health_monitor, pool_id):
        with a10.A10DeleteContext(self, context, health_monitor) as c:
