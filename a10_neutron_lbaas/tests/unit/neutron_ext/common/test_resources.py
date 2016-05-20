# Copyright 2016,  A10 Networks
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

from a10_neutron_lbaas.tests import test_case

from a10_neutron_lbaas.neutron_ext.common import resources


class TestResources(test_case.TestCase):

    def test_apply_template(self):
        template = {
            'none': None,
            'integer': 1,
            'string': 'a string',
            'tuple': ('a tuple', lambda x: x + 1, lambda x: x + 2),
            'dict': {'key': lambda x: x + 3},
            'list': ['a list', lambda x: x + 4]
        }

        actual = resources.apply_template(template, 0)

        expected = {
            'none': None,
            'integer': 1,
            'string': 'a string',
            'tuple': ('a tuple', 1, 2),
            'dict': {'key': 3},
            'list': ['a list', 4]
        }

        self.assertEqual(expected, actual)
