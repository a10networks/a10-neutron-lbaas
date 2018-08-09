# Copyright 2017,  A10 Networks
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

"""

This module includes fake objects used for testing db extensions as well as service plugins.
These classes have primarily been constructed to handle cases in which the data needs to be
tested on in dictionary and object form.

"""


class FakeA10Device(object):

    def __init__(self):
        self.description = 'fake-description'
        self.name = 'fake-name'
        self.nova_instance_id = None
        self.project_id = 'fake-tenant-id'

        self.a10_opts = ['no-autosnat',
                         'no-default_virtual_server_vrid',
                         'no-ipinip',
                         'shared_partition=shared',
                         'no-use_float',
                         'v_method=LSI',
                         'write_memory']
        self.api_version = 'fake-version'
        self.host = 'fake-host'
        self.password = 'fake-password'
        self.port = '442'
        self.protocol = 'https'
        self.username = 'fake-username'

        super(FakeA10Device, self).__init__()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def get_extra_resource_mapping(self):
        mapped_resource = {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:string': None,
            },
            'is_visible': True,
            'default': 'fake-value'
        }
        return mapped_resource


class FakeA10DeviceKey(object):

    def __init__(self):
        self.name = 'fake-name'
        self.description = 'fake-description'

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class FakeA10DeviceValue(object):

    def __init__(self, device_id, key_id):
        self.associated_obj_id = device_id
        self.key_id = key_id
        self.value = 'fake-value'

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class FakeA10vThunder(object):

    def __init__(self):
        self.description = 'fake-description'
        self.name = 'fake-name'
        self.nova_instance_id = None
        self.project_id = 'fake-tenant-id'

        self.api_version = 'fake-version'
        #self.data_networks = ['that_network'],
        #self.flavor = 'MY_FAKE_FLAVOR',
        self.host = 'fake-host'
        #self.image = 'MY_FAKE_IMAGE',
        #self.management_network = 'this_network',
        self.password = 'fake-password'
        self.port = '12345'
        self.protocol = 'https'
        self.username = 'fake-username'

        super(FakeA10vThunder, self).__init__()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)
