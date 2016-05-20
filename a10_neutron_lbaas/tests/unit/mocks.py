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


class FakeModel(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class FakeInstance(dict):
    def __init__(self, **kwargs):
        _default_server = {
            "id": 42,
            "name": None,
            "image": None,
            "flavor": None,
            "meta": {},
            "files": {},
            "min_count": 1,  # optional extension
            "max_count": 1,  # optional extension
            "security_groups": [],
            "userdata": None,
            "key_name": None,  # optional extension
            "availability_zone": None,
            "block_device_mapping": None,  # optional extension
            "block_device_mapping_v2": None,  # optional extension
            "networks": ["mgmt-net"],  # optional extension
            "scheduler_hints": {},  # optional extension
            "config_drive": False,  # optional extension
            "disk_config": "AUTO",   # AUTO or MANUAL # optional extension
            "admin_pass": None  # optional extension
        }

        for k, v in _default_server.iteritems():
            self[k] = kwargs.get(k, _default_server.get(k, None))


class FakeImage(FakeModel):
    def __init__(self, id="image01", name="Image", metadata={}):
        super(FakeImage, self).__init__(id=id, name=name, metadata=metadata)


class FakeFlavor(FakeModel):
    def __init__(self, id="Flavor01", name="Flavor"):
        super(FakeFlavor, self).__init__(id=id, name=name)
