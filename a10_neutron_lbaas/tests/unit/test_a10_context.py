# Copyright 2015,  A10 Networks
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
#    under the License.from neutron.db import model_base

import mock
import unittest

import test_base

import a10_neutron_lbaas.a10_context as a10_context


class TestA10Context(unittest.TestCase):

    def test_a10_context_inventory(self):
        (mock_inventory_class, mock_inventory) = test_base._build_class_instance_mock()
        mock_driver = mock.MagicMock(inventory_class=mock_inventory_class)

        mock_handler = mock.MagicMock(a10_driver=mock_driver)

        mock_appliance = mock.MagicMock()
        mock_appliance.device.return_value = mock.MagicMock()

        mock_inventory.find.return_value = mock_appliance

        target = a10_context.A10Context(
            mock_handler,
            mock.MagicMock(),
            mock.MagicMock(),
            **mock.MagicMock())
        self.assertEqual(mock_inventory, target.inventory)

        with(target):
            self.assertEqual(mock_appliance.device.return_value, target.device_cfg)
