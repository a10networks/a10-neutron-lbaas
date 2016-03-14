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


class StupidSimpleProxy(object):
    def __init__(self, underlying):
        self._underlying = underlying

    def __getattr__(self, attr):
        return getattr(self._underlying, attr)


class ClientProxy(StupidSimpleProxy):
    def __init__(self, underlying_client, device_info):
        super(ClientProxy, self).__init__(underlying_client)
        self._device_info = device_info


class VirtualServer(object):
    """slb.virtual_server mixin"""

    def create(self, name, ip_address, status=1, axapi_body={},
               neutron_subnet_id=None):
        virtual_server = axapi_body.copy()

        vrid = self._device_info.get("default_virtual_server_vrid")
        if vrid is not None:
            virtual_server['vrid'] = vrid

        axapi_args = {'virtual_server': virtual_server}

        return self._underlying.create(
            name,
            ip_address,
            status,
            axapi_args=axapi_args)
