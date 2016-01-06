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

import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.db.operations as db_operations


class TestOperations(test_base.UnitTestBase):

    def operations(self):
        session = self.open_session()
        operations = db_operations.Operations(mock.MagicMock(session=session))
        return operations

    def test_summon_appliance_configured(self):
        operations1 = self.operations()
        appliance1 = operations1.summon_appliance_configured('fake-device-key')
        operations1.session.commit()

        operations2 = self.operations()
        appliance2 = operations2.summon_appliance_configured('fake-device-key')
        operations2.session.commit()

        self.assertEqual(appliance1.id, appliance2.id)

    def test_summon_appliance_configured_distinct(self):
        operations1 = self.operations()
        appliance1 = operations1.summon_appliance_configured('fake-device-key')
        operations1.session.commit()

        operations2 = self.operations()
        appliance2 = operations2.summon_appliance_configured('fake-device-key-2')
        operations2.session.commit()

        self.assertNotEqual(appliance1.id, appliance2.id)

    def test_get_shared_appliances_configured(self):
        operations = self.operations()
        appliance = operations.summon_appliance_configured('fake-device-key')
        shared = operations.get_shared_appliances('fake-tenant')

        self.assertEqual([appliance], shared)

    def test_get_shared_appliances_db_same_tenant(self):
        operations = self.operations()
        appliance = models.default(models.A10ApplianceDB,
                                   tenant_id='fake-tenant',
                                   host='fake-host',
                                   api_version='fake-version',
                                   username='fake-username',
                                   password='fake-password',
                                   protocol='fake-protocol',
                                   port=1234)
        operations.add(appliance)
        shared = operations.get_shared_appliances('fake-tenant')

        self.assertEqual([appliance], shared)

    def test_get_shared_appliances_db_other_tenant(self):
        operations = self.operations()
        appliance = models.default(models.A10ApplianceDB,
                                   tenant_id='other-tenant',
                                   host='fake-host',
                                   api_version='fake-version',
                                   username='fake-username',
                                   password='fake-password',
                                   protocol='fake-protocol',
                                   port=1234)
        operations.add(appliance)
        shared = operations.get_shared_appliances('fake-tenant')

        self.assertEqual([], shared)
