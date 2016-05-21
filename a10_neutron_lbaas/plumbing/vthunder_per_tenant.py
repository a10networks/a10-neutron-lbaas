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

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.vthunder import instance_manager
from a10_neutron_lbaas.vthunder import keystone as a10_keystone

import base


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active, for one vthunder per tenant.

class VThunderPerTenantPlumbingHooks(base.BasePlumbingHooks):

    def _instance_manager(self):
        cfg = self.driver.config
        vth = cfg.get_vthunder_config()
        ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'), vth)
        imgr = instance_manager.InstanceManager(ks_session=ks.session)
        return imgr

    def _create_instance(self, tenant_id, a10_context, lbaas_obj, db_session):
        cfg = self.driver.config
        vth = cfg.get_vthunder_config()
        imgr = self._instance_manager()
        instance = imgr.create_device_instance(vth)

        from a10_neutron_lbaas.etc import defaults
        device_config = {}
        for key in vth:
            if key in ['status', 'ha_sync_list']:
                continue
            if key in defaults.DEVICE_REQUIRED_FIELDS or key in defaults.DEVICE_OPTIONAL_DEFAULTS:
                device_config[key] = vth[key]
        device_config.update({
            'tenant_id': tenant_id,
            'nova_instance_id': instance['nova_instance_id'],
            'name': instance['name'],
            'host': instance['ip_address']
        })

        models.A10DeviceInstance.create_and_save(
            db_session=db_session,
            **device_config)

        return device_config

    def select_device_with_lbaas_obj(self, tenant_id, a10_context, lbaas_obj,
                                     db_session=None):
        if not self.driver.config.get('use_database'):
            raise ex.RequiresDatabase('vThunder orchestration requires use_database=True')

        # If we already have a vThunder, use it.
        # one vthunder per tenant

        tb = models.A10TenantBinding.find_by_tenant_id(tenant_id, db_session=db_session)
        if tb is not None:
            d = self.driver.config.get_device(tb.device_name, db_session=db_session)
            if d is None:
                raise ex.InstanceMissing(
                    'A10 instance mapped to tenant %s is not present in db; '
                    'add it back to config or migrate loadbalancers' % tenant_id)
            return d

        # No? Then we need to create one.

        device_config = self._create_instance(tenant_id, a10_context, lbaas_obj, db_session)

        # Now make sure that we remember where it is.

        models.A10TenantBinding.create_and_save(
            tenant_id=tenant_id,
            device_name=device_config['name'],
            db_session=db_session)

        return device_config

    def after_vip_create(self, a10_context, os_context, vip):
        instance = a10_context.device_cfg
        if 'nova_instance_id' not in instance:
            raise ex.InternalError('Attempting virtual plumbing on non-virtual device')

        if hasattr(vip, 'vip_address'):
            vip_ip_address = vip.vip_address
            vip_subnet_id = vip.vip_subnet_id
        else:
            vip_ip_address = vip['address']
            vip_subnet_id = vip['subnet_id']

        imgr = self._instance_manager()

        return imgr.plumb_instance_subnet(
            instance['nova_instance_id'],
            vip_subnet_id,
            [vip_ip_address],
            wrong_ips=[instance['host']])
