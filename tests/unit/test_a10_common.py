# Copyright 2015, A10 Networks
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

import test_base as test_base

import a10_neutron_lbaas.a10_common as test_target


class TestA10Common(test_base.UnitTestBase):
    def test_bool_to_on_off_positive(self):
        self._test_bool_to_on_off(True, "on")

    def test_bool_to_on_off_negative(self):
        self._test_bool_to_on_off(False, "off")

    def _test_bool_to_on_off(self, boolval, expected_val):
        expected = '"{0}"'.format(expected_val)
        actual = test_target._bool_to_on_off(boolval)
        self.assertEqual(expected, actual)
