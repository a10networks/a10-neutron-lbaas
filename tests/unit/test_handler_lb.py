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

import test_base

import a10_neutron_lbaas.a10_exceptions as a10_ex


class TestLB(test_base.UnitTestBase):

    def test_sanity(self):
        pass

# create no listeners
# create with listeners
# update down
# delete no listeners
# delete with listeners

    def test_refresh(self):
        try:
            self.a.lb.refresh(None, test_base.FakeModel())
        except a10_ex.UnsupportedFeature:
            pass

    def test_stats(self):
        self.a.lb.stats(None, test_base.FakeModel())
        self.print_mocks()
        self.a.last_client.slb.virtual_server.stats.assert_called_with(
            'fake-id-001')
