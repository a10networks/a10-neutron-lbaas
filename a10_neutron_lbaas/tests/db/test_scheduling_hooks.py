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

import test_base

import a10_neutron_lbaas.db.operations as db_operations
import a10_neutron_lbaas.inventory as inventory
import a10_neutron_lbaas.scheduling_hooks as scheduling_hooks


class TestDevicePerTenant(test_base.UnitTestBase):

    def a10_context(self):
        session = self.open_session()
        operations = db_operations.Operations(mock.MagicMock(session=session))

        a10 = mock.MagicMock(
            db_operations=operations,
            openstack_context=mock.MagicMock(session=session))
        a10.a10_driver.config.devices.__getitem__.side_effect = lambda x: {'key': x}

        a10.inventory = inventory.InventoryBase(a10)

        return a10

    def test_select_appliance_remembers_tenant_appliance(self):
        a10 = self.a10_context()
        a10.tenant_id = 'fake-tenant-id'

        mock1 = mock.MagicMock()
        mock1.select_devices.return_value = [{
            'host': 'fake-host',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password'}]
        target1 = scheduling_hooks.DevicePerTenant(mock1)
        devices1 = target1.select_devices(a10, [])
        device1 = next(devices1.__iter__())

        mock2 = mock.MagicMock()
        target2 = scheduling_hooks.DevicePerTenant(mock2)
        devices2 = target2.select_devices(a10, [])
        device2 = next(devices2.__iter__())

        mock2.select_devices.assert_not_called()

        self.assertEqual(device1, device2)
