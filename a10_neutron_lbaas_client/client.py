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
#    under the License.

from neutronclient.v2_0 import client as clientbase

from a10_neutron_lbaas_client.resources import a10_appliance


class Client(clientbase.Client):
    a10_appliances_path = "/%s" % a10_appliance.RESOURCE
    a10_appliance_path = "/%s/%%s" % a10_appliance.RESOURCE

    @clientbase.APIParamsCall
    def list_a10_appliances(self, **_params):
        return self.get(self.a10_appliances_path, params=_params)

    @clientbase.APIParamsCall
    def show_a10_appliance(self, id, **_params):
        return self.get(self.a10_appliance_path % id, params=_params)

    @clientbase.APIParamsCall
    def create_a10_appliance(self, body=None):
        return self.post(self.a10_appliances_path, body=body)

    @clientbase.APIParamsCall
    def update_a10_appliance(self, body=None):
        id = body['a10_appliance']['id']
        return self.put(self.a10_appliance_path % id, body=body)

    @clientbase.APIParamsCall
    def delete_a10_appliance(self, id):
        return self.delete(self.a10_appliance_path % id)
