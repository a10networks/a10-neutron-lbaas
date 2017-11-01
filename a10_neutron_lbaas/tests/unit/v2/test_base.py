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


class UnitTestBase(test_base.UnitTestBase):

    def __init__(self, *args):
        super(UnitTestBase, self).__init__(*args)
        self.version = 'v2'

    def print_mocks(self):
        super(UnitTestBase, self).print_mocks()
        print("NEUTRON ", self.a.neutron.mock_calls)


class HandlerTestBase(UnitTestBase):
    def __init__(self, *args):
        super(HandlerTestBase, self).__init__(*args)

    def _get_expressions_mock(self):
        return {
            # Start match
            "^secure": {
                "no-logging": 1,
                "template-virtual-port": "default"
            },
            # End match
            ".*?web$": {
                "scaleout-bucket-count": 32
            },
            # character class
            "[w]{1,3}": {
                "scaleout-bucket-count": 64
            }
        }
