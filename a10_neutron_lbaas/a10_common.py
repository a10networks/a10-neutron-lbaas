# Copyright 2015 A10 Networks
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

auto_dictionary = {
    "2.1": ("source_nat_auto", lambda x: int(x)),
    "3.0": ("auto", lambda x: x)
}


def _set_auto_parameter(vport, device_info):
    api_ver = device_info.get("api_version", None)
    auto_tuple = auto_dictionary.get(api_ver, None)

    vport_key = None
    vport_transform = lambda x: x

    if auto_tuple:
        vport_key = auto_tuple[0]
        vport_transform = auto_tuple[1]

    if vport_key is not None:
        cfg_value = device_info.get("autosnat", False)
        vport[vport_key] = vport_transform(cfg_value)


def _set_vrid_parameter(virtual_server, device_info):
    vrid = device_info.get("default_virtual_server_vrid", None)

    if vrid is not None:
        virtual_server['vrid'] = vrid


def _set_ipinip_parameter(vport, device_info):
    key = "ip_in_ip"
    ipinip = device_info.get(key, False)
    if ipinip:
        vport[key] = int(ipinip)
