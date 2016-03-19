# Copyright 2014, A10 Networks
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

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import api as db_api
from a10_neutron_lbaas.db import models


class PlumbingHooks(object):

    def __init__(self, driver, devices=None):
        self.driver = driver
        if devices is not None:
            self.devices = devices
        else:
            self.devices = self.driver.config.devices
        self.appliance_hash = acos_client.Hash(self.devices.keys())

    def select_device_hash(self, tenant_id):
        # Must return device dict from config.py
        s = self.appliance_hash.get_server(tenant_id)
        return self.devices[s]

    def select_device_db(self, tenant_id, db_session=None):
        if db_session is not None:
            db = db_session
        else:
            db = db_api.get_session()

        # See if we have a saved tenant
        a10 = db.query(models.A10TenantBinding).filter(
            models.A10TenantBinding.tenant_id == tenant_id).one_or_none()
        if a10 is not None:
            if a10.device_name in self.devices:
                return self.devices[a10.device_name]
            else:
                raise ex.DeviceConfigMissing(
                    'A10 device %s mapped to tenant %s is not present in config; '
                    'add it back to config or migrate loadbalancers' %
                    (a10.device_name, tenant_id))

        # Nope, so we hash and save
        d = self.select_device_hash(tenant_id)
        a10 = models.A10TenantBinding(tenant_id=tenant_id, device_name=d['name'])
        db.add(a10)
        db.commit()
        return d

    def select_device(self, tenant_id):
        if self.driver.config.use_database:
            return self.select_device_db(tenant_id)
        else:
            return self.select_device_hash(tenant_id)

    def partition_create(self, client, context, partition_name):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, context, partition_name):
        client.system.partition.delete(partition_name)

    def after_member_create(self, client, context, member):
        pass

    def after_member_update(self, client, context, member):
        pass

    def after_member_delete(self, client, context, member):
        pass

    def after_vip_create(self, client, context, vip):
        pass

    def after_vip_update(self, client, context, vip):
        pass

    def after_vip_delete(self, client, context, vip):
        pass
