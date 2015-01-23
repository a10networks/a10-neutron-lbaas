# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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

import json


class HandlerBase(object):

    def __init__(self, a10_driver):
        self.a10_driver = a10_driver
        self.hooks = a10_driver.hooks
        self.openstack_driver = self.a10_driver.openstack_driver

    def meta(self, lbaas_obj, key, default):
        m = lbaas_obj.get('a10_meta', '{}')
        try:
            d = json.loads(m)
        except Exception:
            return default
        return d.get(key, default)
