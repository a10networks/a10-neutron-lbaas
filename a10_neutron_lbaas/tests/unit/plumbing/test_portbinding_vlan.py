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

import mock

from a10_neutron_lbaas.tests.unit import test_base

from a10_neutron_lbaas.plumbing import portbinding_vlan 


class FakeConfig(object):
    def __init__(self, *args, **kwargs):
        self._dict = kwargs

    def get(self, key):
        return self._dict.get(key)

class TestVlanPortBindingPlumbing(test_base.UnitTestBase):
    version = "v2"

    def setUp(self, *args, **kwargs):
        super(TestVlanPortBindingPlumbing, self).setUp(*args, **kwargs)
        config = self._build_config_mock(use_database=False)
        driver = self._build_driver_mock(config=config)
        devices = {"a": {"host": "1.2.3.4"}}
        self.os_context = test_base._build_openstack_context()
        self.a10_context = mock.Mock()
        self.target = portbinding_vlan.VlanPortBindingPlumbingHooks(driver, devices)

    def test_select_device(self):

        a = self.target.select_device("first-token")
        self.target.select_device("second-token")
        self.assertEqual(a, self.target.select_device("first-token"))

    def test_after_vip_create(self):
        vip = mock.Mock()
        self.target.after_vip_create(self.a10_context, self.os_context, vip)

    def _build_config_mock(self, **kwargs):
        return FakeConfig(**kwargs) 

    def _build_driver_mock(self, **kwargs):
        rval = mock.Mock(**kwargs)

        return rval

