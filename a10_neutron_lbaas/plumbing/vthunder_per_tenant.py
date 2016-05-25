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

import errno
import logging
import time

import acos_client

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.vthunder import instance_initialization
from a10_neutron_lbaas.vthunder import instance_manager

import base

LOG = logging.getLogger(__name__)


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active, for one vthunder per tenant.

class VThunderPerTenantPlumbingHooks(base.BasePlumbingHooks):

    def get_a10_client(self, device_info, **kwargs):
        if kwargs.get('action', None) == 'create':
            retry = [errno.EHOSTUNREACH, errno.ECONNRESET, errno.ECONNREFUSED, errno.ETIMEDOUT]
            return acos_client.Client(
                device_info['host'], device_info['api_version'],
                device_info['username'], device_info['password'],
                port=device_info['port'], protocol=device_info['protocol'],
                retry_errno_list=retry)
        else:
            return super(VThunderPerTenantPlumbingHooks, self).get_a10_client(device_info, **kwargs)

    def _instance_manager(self, a10_context):
        return instance_manager.InstanceManager.from_config(
            self.driver.config, a10_context.openstack_context)

    def _create_instance(self, tenant_id, a10_context, lbaas_obj, db_session):
        start = time.time()
        cfg = self.driver.config
        vth = cfg.get_vthunder_config()
        imgr = self._instance_manager(a10_context)
        instance = imgr.create_device_instance(vth)
        end = time.time()

        LOG.debug("A10 vThunder %s: spawned after %d seconds", instance['nova_instance_id'],
                  end - start)

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
            'host': instance['ip_address'],
        })

        models.A10DeviceInstance.create_and_save(
            db_session=db_session,
            **device_config)

        device_config.update({
            '_perform_initialization': True
        })
        return device_config

    def _wait_for_instance(self, device_config):
        start = time.time()
        client = self.get_a10_client(device_config)
        client.wait_for_connect()
        end = time.time()

        # XXX(dougwig) - this is a <=4.1.0 after CM bug is fixed
        time.sleep(5.0)

        LOG.debug("A10 vThunder %s: ready to connect after %d seconds",
                  device_config['nova_instance_id'], end - start)

    def select_device_with_lbaas_obj(self, tenant_id, a10_context, lbaas_obj,
                                     db_session=None, **kwargs):
        if not self.driver.config.get('use_database'):
            raise ex.RequiresDatabase('vThunder orchestration requires use_database=True')

        # If we already have a vThunder, use it.
        # one vthunder per tenant

        missing_instance = (
            'A10 instance mapped to tenant %s is not present in db; '
            'add it back to config or migrate loadbalancers' % tenant_id
        )

        tb = models.A10TenantBinding.find_by_tenant_id(tenant_id, db_session=db_session)
        if tb is not None:
            d = self.driver.config.get_device(tb.device_name, db_session=db_session)
            if d is None:
                LOG.error(missing_instance)
                raise ex.InstanceMissing(missing_instance)

            LOG.debug("select_device, returning cached instance %s", d)
            return d

        # No? Then we need to create one.

        if kwargs.get('action') != 'create':
            LOG.error(missing_instance)
            raise ex.InstanceMissing(missing_instance)

        device_config = self._create_instance(tenant_id, a10_context, lbaas_obj, db_session)
        self._wait_for_instance(device_config)

        # Now make sure that we remember where it is.

        models.A10TenantBinding.create_and_save(
            tenant_id=tenant_id,
            device_name=device_config['name'],
            db_session=db_session)

        LOG.debug("select_device, returning new instance %s", device_config)
        return device_config

    def after_select_partition(self, a10_context):
        instance = a10_context.device_cfg
        client = a10_context.client

        LOG.debug("after_select_partition, checking instance %s", instance)

        if instance.get('_perform_initialization'):
            instance_initialization.initialize_vthunder(
                a10_context.a10_driver.config, instance, client)

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

        imgr = self._instance_manager(a10_context)
        return imgr.plumb_instance_subnet(
            instance['nova_instance_id'],
            vip_subnet_id,
            [vip_ip_address],
            wrong_ips=[instance['host']])
