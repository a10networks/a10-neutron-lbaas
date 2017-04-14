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
        self.EXPR_BEGIN = "beginning"
        self.EXPR_END = "end"
        self.EXPR_CLASS = "charclass"

    def _get_expressions_mock(self):
        return {
            self.EXPR_BEGIN: {
                "regex": "^secure",
                "json": {
                    "template-virtual-port": "default",
                    "no-logging": 1,
                },
            },
            self.EXPR_END: {
                "regex": ".*?web$",
                "json": {
                    "scaleout-bucket-count": 32
                },
            },
            self.EXPR_CLASS: {
                "regex": "[w]{2,3}",
                "json": {
                    "scaleout-bucket-count": 64
                }
            }
        }
