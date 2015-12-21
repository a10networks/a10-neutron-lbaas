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

from neutronclient.v2_0 import client as clientbase

import a10_neutron_lbaas.neutron_ext.extensions.a10Appliance as a10Appliance
import a10_neutron_lbaas.neutron_ext.extensions.a10Image as a10Image


class Client(clientbase.Client):
    a10_appliances_path = "/%s" % a10Appliance.A10_APPLIANCE_RESOURCE
    a10_appliance_path = "/%s/%%s" % a10Appliance.A10_APPLIANCE_RESOURCE

    a10_images_path = "/%s" % a10Image.A10_IMAGE_RESOURCE
    a10_image_path = "/%s/%%s" % a10Image.A10_IMAGE_RESOURCE

    # Appliances
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

    # Images
    @clientbase.APIParamsCall
    def list_a10_images(self, **_params):
        return self.get(self.a10_images_path, params=_params)

    @clientbase.APIParamsCall
    def show_a10_image(self, id, **_params):
        return self.get(self.a10_image_path % id, params=_params)

    @clientbase.APIParamsCall
    def create_a10_image(self, body=None):
        return self.post(self.a10_images_path, body=body)

    @clientbase.APIParamsCall
    def update_a10_image(self, body=None):
        id = body['a10_image']['id']
        return self.put(self.a10_image_path % id, body=body)

    @clientbase.APIParamsCall
    def delete_a10_image(self, id):
        return self.delete(self.a10_image_path % id)
