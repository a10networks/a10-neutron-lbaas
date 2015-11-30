# Copyright (C) 2015, A10 Networks Inc. All rights reserved.
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

import a10_neutron_lbaas.tests.test_case as test_case

import a10_neutron_lbaas.db.migration.mocks as mocks


class TestMocks(test_case.TestCase):

    def test_uncallable(self):
        mock = mocks.UncallableMock()
        self.assertRaises(NotImplementedError, mock)

    def test_member_same_twice(self):
        mock = mocks.UncallableMock()
        mock1 = mock.some_member
        mock2 = mock.some_member

        self.assertEqual(mock1, mock2)

    def test_member_uncallable(self):
        mock = mocks.UncallableMock()
        self.assertRaises(NotImplementedError, mock.some_member)

    def test_item_same_twice(self):
        mock = mocks.UncallableMock()
        mock1 = mock['some_item']
        mock2 = mock['some_item']

        self.assertEqual(mock1, mock2)

    def test_item_uncallable(self):
        mock = mocks.UncallableMock()
        self.assertRaises(NotImplementedError, mock['some_item'])

    def test_str(self):
        mock = mocks.UncallableMock()
        self.assertIsNot(str(mock), None)

    def test_repr(self):
        mock = mocks.UncallableMock()
        self.assertIsNot(repr(mock), None)

    def test_member_name(self):
        mock = mocks.UncallableMock('fake_name')
        member = mock.some_member
        self.assertEqual('fake_name.some_member', repr(member))

    def test_item_name(self):
        mock = mocks.UncallableMock('fake_name')
        item = mock['some_item']
        self.assertEqual("fake_name['some_item']", repr(item))
