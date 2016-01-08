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

from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.db import operations as db_operations


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

    def test_delete_slb_v1_deletes_slb(self):
        slb = models.default(
            models.A10SLBV1,
            vip_id='fake-vip-id',
            a10_appliance_id='fake-a10-appliance-id'
        )

        operations1 = self.operations()
        operations1.add(slb)
        operations1.session.commit()

        operations2 = self.operations()
        operations2.delete_slb_v1(slb.vip_id)
        operations2.session.commit()

        session = self.open_session()
        slbs = list(session.query(models.A10SLB))

        self.assertEqual([], slbs)

    def test_delete_slb_v2_deletes_slb(self):
        slb = models.default(
            models.A10SLBV2,
            lbaas_loadbalancer_id='lbaas_loadbalancer_id',
            a10_appliance_id='fake-a10-appliance-id'
        )

        operations1 = self.operations()
        operations1.add(slb)
        operations1.session.commit()

        operations2 = self.operations()
        operations2.delete_slb_v2(slb.lbaas_loadbalancer_id)
        operations2.session.commit()

        session = self.open_session()
        slbs = list(session.query(models.A10SLB))

        self.assertEqual([], slbs)
