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
 

def device_acos_client(device_info):
    d = device_info
    return acos_client.Client(d['host'],
                              d.get('api_version', acos_client.AXAPI_21),
                              d['username'], d['password'],
                              port=d['port'], protocol=d['protocol'])

class UniformDeviceClient(object):
	def __init__(self, client_factory=device_acos_client):
		self.client_factory = client_factory

	def __call__(self, device_info):
		return self.client_factory(device_info)
