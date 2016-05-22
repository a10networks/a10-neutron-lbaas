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
#    under the License.

import acos_client

from a10_neutron_lbaas.db import models
import a10_neutron_lbaas.plumbing_hooks as hooks

import test_base

dev1 = {'name': 'dev1'}
dev2 = {'name': 'dev2'}
dev3 = {'name': 'dev3'}
dev4 = {'name': 'dev4'}
dev5 = {'name': 'dev5'}
dev6 = {'name': 'dev6'}

devices1 = {'dev1': dev1}
devices2 = {
    'dev1': dev1,
    'dev2': dev2,
    'dev3': dev3,
    'dev4': dev4,
    'dev5': dev5,
    'dev6': dev6,
}

TENANT_ID = 'xxx'

EXPECTED_DEV1 = acos_client.Hash(devices1.keys()).get_server(TENANT_ID)
HARDCODE_RESULT1 = 'dev1'
EXPECTED_DEV2 = acos_client.Hash(devices2.keys()).get_server(TENANT_ID)
HARDCODE_RESULT2 = 'dev2'


class TestSelectDevice(test_base.UnitTestBase):

    def test_test_setup(self):
        self.assertEqual(EXPECTED_DEV1, HARDCODE_RESULT1)
        self.assertEqual(EXPECTED_DEV2, HARDCODE_RESULT2)
        self.assertNotEqual(EXPECTED_DEV1, EXPECTED_DEV2)

    def test_select_device_hash(self):
        h = hooks.PlumbingHooks(None, devices=devices1)
        d = h._select_device_hash(TENANT_ID)
        self.assertEqual(d['name'], EXPECTED_DEV1)

        h = hooks.PlumbingHooks(None, devices=devices2)
        d = h._select_device_hash(TENANT_ID)
        self.assertEqual(d['name'], EXPECTED_DEV2)

    def test_select_device_db(self):
        h = hooks.PlumbingHooks(None, devices=devices1)
        db = self.open_session()
        d = h._select_device_db(TENANT_ID, db_session=db)
        self.assertEqual(d['name'], EXPECTED_DEV1)

        db = self.open_session()
        z = list(db.query(models.A10TenantBinding))
        self.assertEqual(z[0].tenant_id, TENANT_ID)
        self.assertEqual(z[0].device_name, EXPECTED_DEV1)

        h = hooks.PlumbingHooks(None, devices=devices2)
        db = self.open_session()
        d = h._select_device_db(TENANT_ID, db_session=db)
        self.assertEqual(d['name'], EXPECTED_DEV1)  # 1 is not a typo
