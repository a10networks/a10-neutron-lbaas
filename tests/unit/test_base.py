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

import unittest

import mock

import a10_neutron_lbaas


class FakeModel(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'fake-id-001')
        self.tenant_id = kwargs.get('tenant_id', 'get-off-my-lawn')


class FakeLB(FakeModel):
    pass


class FakeListener(FakeModel):
    pass


class FakePool(FakeModel):
    pass


class FakeMember(FakeModel):
    pass


class FakeHM(FakeModel):
    pass


class FakeA10OpenstackLB(a10_neutron_lbaas.A10OpenstackLB):

    def __init__(self, openstack_driver):
        super(FakeA10OpenstackLB, self).__init__(mock.MagicMock())

    def _get_a10_client(self, device_info):
        return mock.MagicMock()


class UnitTestBase(unittest.TestCase):

    def setUp(self):
        self.a = FakeA10OpenstackLB(None)
