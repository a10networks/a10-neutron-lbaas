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

import a10_neutron_lbaas.tests.db.test_base as test_base

import a10_neutron_lbaas.db.operations as db_operations
import a10_neutron_lbaas.v1.inventory as inventory


class TestInventory(test_base.UnitTestBase):

    def inventory(self):
        session = self.open_session()
        operations = db_operations.Operations(mock.MagicMock(session=session))

        a10_context = mock.MagicMock(
            db_operations=operations,
            openstack_context=mock.MagicMock(session=session))

        return inventory.InventoryV1(a10_context)

    def test_find_selects_appliance(self):
        target = self.inventory()
        appliance = target.db_operations.summon_appliance_configured('fake-device-key')
        target.a10_context.tenant_id = 'fake-tenant-id'
        target.a10_context.a10_driver._select_a10_device.return_value = {'key': 'fake-device-key'}

        openstack_lbaas_object = mock.MagicMock()
        found_appliance = target.find(openstack_lbaas_object)

        self.assertEqual(appliance, found_appliance)

    def test_find_remembers_appliance(self):
        target1 = self.inventory()
        target1.a10_context.tenant_id = 'fake-tenant-id'
        target1.a10_context.a10_driver._select_a10_device.return_value = {'key': 'fake-device-key'}

        openstack_lbaas_object = mock.MagicMock()
        target1.find(openstack_lbaas_object)
        target1.db_operations.session.commit()

        target2 = self.inventory()
        target2.a10_context.tenant_id = 'fake-tenant-id'
        target2.a10_context.a10_driver._select_a10_device.return_value = {'key': 'other-device-key'}
        found_appliance = target2.find(openstack_lbaas_object)

        self.assertEqual('fake-device-key', found_appliance.device_key)
