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
    "3.0": ("auto", lambda x: int(x))
}

ipinip_dictionary = {
    "2.1": ("ip_in_ip", lambda x: int(x)),
    "3.0": ("ipinip", lambda x: int(x))
}


vport_dictionary = {
    "2.1": "vport",
    "3.0": "port"
}


def _api_ver(device_info):
    api_ver = device_info.get("api_version", None)
    if api_ver is None:
        api_ver = "2.1"
    return api_ver


def _set_auto_parameter(vport, device_info):
    api_ver = _api_ver(device_info)
    auto_tuple = auto_dictionary.get(api_ver, None)

    if auto_tuple:
        (vport_key, vport_transform) = auto_tuple

    if vport_key is not None:
        cfg_value = device_info.get("autosnat", False) or False
        vport[vport_key] = vport_transform(cfg_value)


def _set_vrid_parameter(virtual_server, device_info):
    vrid = device_info.get("default_virtual_server_vrid")

    if vrid is not None:
        virtual_server['vrid'] = vrid


def _set_ipinip_parameter(vport, device_info):
    config_key = "ipinip"
    api_ver = device_info.get("api_version", None)
    ipinip_tuple = ipinip_dictionary.get(api_ver, None)
    key = None

    transform = lambda x: x

    if ipinip_tuple:
        (key, transform) = ipinip_tuple

    ipinip = device_info.get(config_key, False) or False

    if key is not None and ipinip:
        vport[key] = transform(ipinip)


def _vport(vport_meta, device_info):
    api_ver = _api_ver(device_info)

    _set_auto_parameter(vport_meta, device_info)
    _set_ipinip_parameter(vport_meta, device_info)

    key = vport_dictionary[api_ver]
    vport = {key: vport_meta}
    return vport


def _virtual_server(virtual_server_meta, device_info):
    _set_vrid_parameter(virtual_server_meta, device_info)

    virtual_server = {'virtual_server': virtual_server_meta}
    return virtual_server
