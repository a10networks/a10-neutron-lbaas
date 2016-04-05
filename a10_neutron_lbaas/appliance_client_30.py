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


class Client(appliance_client_base.ClientProxy):

    @property
    def slb(self):
        return SLB(self._underlying.slb, self._device_info)


class SLB(appliance_client_base.ClientProxy):

    @property
    def virtual_server(self):
        return VirtualServer(self._underlying.virtual_server, self._device_info)


class VirtualServer(appliance_client_base.VirtualServer, appliance_client_base.ClientProxy):

    @property
    def vport(self):
        return VPort(self._underlying.vport, self._device_info)


class VPort(appliance_client_base.ClientProxy):

    def _vport_args(self, axapi_body):

        vport = axapi_body.copy()

        autosnat = self._device_info.get("autosnat", False) or False
        vport["auto"] = int(autosnat)

        ipinip = self._device_info.get("ipinip", False) or False
        if ipinip:
            vport["ipinip"] = int(ipinip)

        axapi_args = {"port": vport}

        return axapi_args

    def create(self, virtual_server_name, name, protocol, port,
               service_group_name,
               s_pers_name=None, c_pers_name=None, status=1,
               axapi_body={}, **kwargs):

        axapi_args = self._vport_args(axapi_body)

        return self._underlying.create(
            virtual_server_name, name,
            protocol=protocol, port=port, service_group_name=service_group_name,
            s_pers_name=s_pers_name, c_pers_name=c_pers_name, status=status,
            axapi_args=axapi_args, **kwargs)

    def update(self, virtual_server_name, name, protocol, port,
               service_group_name,
               s_pers_name=None, c_pers_name=None, status=1,
               axapi_body={}, **kwargs):

        axapi_args = self._vport_args(axapi_body)

        return self._underlying.update(
            virtual_server_name, name,
            protocol=protocol, port=port, service_group_name=service_group_name,
            s_pers_name=s_pers_name, c_pers_name=c_pers_name, status=status,
            axapi_args=axapi_args, **kwargs)
