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

import a10_neutron_lbaas.tests.unit.test_base as test_base


class FakeModel(dict, object):
    def __getitem__(self, key, default=None):
        attr = getattr(self, key, default)
        return attr

    def get(self, key, default=None):
        return getattr(self, key, default)

    # def copy(self):
    #     import copy
    #     return copy.deepcopy(self)


class FakeHM(FakeModel):
    def __init__(self, id="hm01", name="hm01"):
        self.id = id
        self.name = name
        self.pools = []


class FakePool(FakeModel):
    def __init__(self, id="p01", name="p01"):
        self.id = id
        self.name = name


class UnitTestBase(test_base.UnitTestBase):

    def __init__(self, *args):
        super(UnitTestBase, self).__init__(*args)
        self.version = 'v1'
