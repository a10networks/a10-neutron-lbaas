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

import datetime

from a10_neutron_lbaas.db import models

import test_base

dt = datetime.datetime.fromtimestamp(1458346727.132739)


class TestTenantBindings(test_base.UnitTestBase):

    def test_model_create(self):
        db = self.open_session()
        x = models.A10TenantBinding(
            tenant_id='xxx',
            device_name='yyy',
            created_at=dt)
        db.add(x)
        db.commit()

        db = self.open_session()
        z = list(db.query(models.A10TenantBinding))
        self.assertEqual(len(z), 1)
        self.assertEqual(z[0].tenant_id, 'xxx')
        self.assertEqual(z[0].device_name, 'yyy')
        self.assertTrue(len(z[0].id) == 36)
        self.assertEqual(z[0].created_at, dt)

        db = self.open_session()
        x = models.A10TenantBinding.create_and_save(
            tenant_id='xxx2',
            device_name='yyy2',
            created_at=dt,
            db_session=db)

        db = self.open_session()
        t = models.A10TenantBinding.find_by_tenant_id('xxx2', db_session=db)
        self.assertEqual(t.device_name, 'yyy2')
