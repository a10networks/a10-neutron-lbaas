# Copyright 2016, A10 Networks
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

import appliance_client_base
import instance_manager


class NovaPlumber(object):
    def __init__(self, nova_instance_id, instance_manager):
        self.nova_instance_id = nova_instance_id,
        self.instance_manager = instance_manager

    def plumb(self, subnet_id, ip_address):
        return self.instance_manager.plumb_instance_subnet(
            self.nova_instance_id,
            subnet_id,
            ip_address)


def plumbed_client(underlying_client, context, nova_instance_id):
    im = instance_manager.context_instance_manager(context)
    plumber = NovaPlumber(nova_instance_id, im)
    client = Client(underlying_client, plumber)
    return client


class ClientProxy(appliance_client_base.StupidSimpleProxy):
    def __init__(self, underlying_client, plumber):
        super(ClientProxy, self).__init__(underlying_client)
        self._plumber = plumber


class Client(ClientProxy):

    @property
    def slb(self):
        return SLB(self._underlying.slb, self._plumber)


class SLB(ClientProxy):

    @property
    def virtual_server(self):
        return VirtualServer(self._underlying.virtual_server, self._plumber)


class VirtualServer(ClientProxy):

    def create(self, name, ip_address, status=1, neutron_subnet_id=None, **kwargs):

        result = self._underlying.create(name, ip_address, status=status, **kwargs)

        self._plumber.plumb(neutron_subnet_id, [ip_address])

        return result
