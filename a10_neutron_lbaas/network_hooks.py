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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NetworkHooks(object):
    """Interface for network hooks"""

    @abc.abstractmethod
    def partition_create(self, client, a10_context, context, partition_name):
        pass

    @abc.abstractmethod
    def partition_delete(self, client, a10_context, context, partition_name):
        pass

    @abc.abstractmethod
    def after_member_create(self, a10_context, context, member):
        pass

    @abc.abstractmethod
    def after_member_update(self, a10_context, context, member):
        pass

    @abc.abstractmethod
    def after_member_delete(self, a10_context, context, member):
        pass

    @abc.abstractmethod
    def after_vip_create(self, a10_context, context, vip):
        pass

    @abc.abstractmethod
    def after_vip_update(self, a10_context, context, vip):
        pass

    @abc.abstractmethod
    def after_vip_delete(self, a10_context, context, vip):
        pass


class DefaultNetworkHooksMixin(NetworkHooks):

    def partition_create(self, client, a10_context, context, partition_name):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, a10_context, context, partition_name):
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


class DefaultNetworkHooks(DefaultNetworkHooksMixin):

    def __init__(self, a10_driver):
        pass


class PlumbingNetworkHooks(NetworkHooks):

    def __init__(self, plumbing_hooks):
        self.plumbing_hooks = plumbing_hooks

    def partition_create(self, client, a10_context, context, partition_name):
        self.plumbing_hooks.partition_create(client, context, partition_name)

    def partition_delete(self, client, a10_context, context, partition_name):
        self.plumbing_hooks.partition_delete(client, context, partition_name)

    def after_member_create(self, a10_context, context, member):
        self.plumbing_hooks.after_member_create(a10_context, context, member)

    def after_member_update(self, a10_context, context, member):
        self.plumbing_hooks.after_member_update(a10_context, context, member)

    def after_member_delete(self, a10_context, context, member):
        self.plumbing_hooks.after_member_delete(a10_context, context, member)

    def after_vip_create(self, a10_context, context, vip):
        self.plumbing_hooks.after_vip_create(a10_context, context, vip)

    def after_vip_update(self, a10_context, context, vip):
        self.plumbing_hooks.after_vip_update(a10_context, context, vip)

    def after_vip_delete(self, a10_context, context, vip):
        self.plumbing_hooks.after_vip_delete(a10_context, context, vip)


def plumbing_network_hooks(plumbing_hooks):
    return lambda a10_driver: PlumbingNetworkHooks(plumbing_hooks)
