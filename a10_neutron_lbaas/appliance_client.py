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

import acos_client
import appliance_client_21
import appliance_client_30


def device_acos_client(device_info):
    d = device_info
    return acos_client.Client(d['host'],
                              d.get('api_version', acos_client.AXAPI_21),
                              d['username'], d['password'],
                              port=d['port'], protocol=d['protocol'])


def _api_ver(device_info):
    api_ver = device_info.get("api_version", None)
    if api_ver is None:
        api_ver = "2.1"
    return api_ver


version_adapters = {
    "2.1": appliance_client_21.Client,
    "3.0": appliance_client_30.Client
}


def uniform_device_client(underlying_client, device_info):
    api_ver = _api_ver(device_info)
    proxy = version_adapters.get(api_ver, lambda x, d: x)
    client = proxy(underlying_client, device_info)

    return client
