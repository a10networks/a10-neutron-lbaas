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


class Device(object):
    url_prefix = '/agapi/v1/device/'

    def __init__(self, client):
        self.session = client.session

    def all(self):
        device_envelope = self.session.get(self.url_prefix)

        if device_envelope is None:
            return []

        return device_envelope['device_list']

    # This isn't documented ...
    def get(self, id):
        return self.session.get(self.url_prefix + id + '/')

    def create(self, device):
        return self.session.post(self.url_prefix, device)

    # This isn't documented ...
    # def update(self, id, device):
    #    return self.session.put(self.url_prefix + id, device)

    # This isn't documented ...
    def delete(self, id):
        return self.session.delete(self.url_prefix + id + '/')
