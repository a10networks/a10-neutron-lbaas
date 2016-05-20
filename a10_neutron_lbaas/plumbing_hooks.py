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
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.vthunder import instance_manager
from a10_neutron_lbaas.vthunder import keystone as a10_keystone


class BasePlumbingHooks(object):

    def __init__(self, driver, **kwargs):
        self.driver = driver
        self.client_wrapper_class = None

    # While you can override select_device in hooks to get custom selection
    # behavior, it is much easier to use the 'device_scheduling_filters'
    # mechanism, as documented in the config file.

    def select_device(self, tenant_id):
        # Not a terribly useful scheduler
        raise ex.NotImplemented()

    # Network plumbing hooks from here on out

    def partition_create(self, client, os_context, partition_name):
        client.system.partition.create(partition_name)

    def partition_delete(self, client, os_context, partition_name):
        client.system.partition.delete(partition_name)

    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def after_member_delete(self, a10_context, os_context, member):
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        pass

    def after_vip_update(self, a10_context, os_context, vip):
        pass

    def after_vip_delete(self, a10_context, os_context, vip):
        pass


# The default set of plumbing hooks/scheduler, meant for hardware or manual orchestration

class PlumbingHooks(BasePlumbingHooks):

    def __init__(self, driver, devices=None, get_devices_func=None, **kwargs):
        super(PlumbingHooks, self).__init__(
            driver, devices=devices, get_devices_func=get_devices_func, **kwargs)
        if devices is not None:
            self.devices = devices
        elif get_devices_func is not None:
            self.devices = get_devices_func()
        else:
            self.devices = None
        self.appliance_hash = None

    def _late_init(self):
        if self.devices is None:
            self.devices = self.driver.config.get_devices()
        if self.appliance_hash is None:
            self.appliance_hash = acos_client.Hash(self.devices.keys())

    def _select_device_hash(self, tenant_id):
        self._late_init()

        # Must return device dict from config.py
        s = self.appliance_hash.get_server(tenant_id)
        return self.devices[s]

    def _select_device_db(self, tenant_id, db_session=None):
        self._late_init()

        # See if we have a saved tenant
        a10 = models.A10TenantBinding.find_by_tenant_id(tenant_id, db_session=db_session)
        if a10 is not None:
            if a10.device_name in self.devices:
                return self.devices[a10.device_name]
            else:
                raise ex.DeviceConfigMissing(
                    'A10 device %s mapped to tenant %s is not present in config; '
                    'add it back to config or migrate loadbalancers' %
                    (a10.device_name, tenant_id))

        # Nope, so we hash and save
        d = self._select_device_hash(tenant_id)
        models.A10TenantBinding.create_and_save(
            tenant_id=tenant_id, device_name=d['name'],
            db_session=db_session)

        return d

    def select_device(self, tenant_id):
        if self.driver.config.get('use_database'):
            return self._select_device_db(tenant_id)
        else:
            return self._select_device_hash(tenant_id)


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active.

class VThunderPlumbingHooks(PlumbingHooks):

    def _instance_manager(self):
        cfg = self.driver.config
        vth = cfg.get_vthunder_config()
        ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'), vth)
        imgr = instance_manager.InstanceManager(ks_session=ks.session)
        return imgr

    def select_device_with_lbaas_obj(self, tenant_id, a10_context, lbaas_obj,
                                     db_session=None):
        if not self.driver.config.get('use_database'):
            raise ex.RequiresDatabase('vThunder orchestration requires use_database=True')

        # If we already have a vThunder, use it.

        if hasattr(lbaas_obj, 'root_loadbalancer'):
            # lbaas v2
            root_id = lbaas_obj.root_loadbalancer.id
            slb = models.A10SLB.find_by(loadbalancer_id=root_id, db_session=db_session)
            if slb is not None:
                d = self.driver.config.get_device(slb.device_name, db_session=db_session)
                if d is None:
                    raise ex.InstanceMissing(
                        'A10 instance mapped to loadbalancer_id %s is not present in db; '
                        'add it back to config or migrate loadbalancers' % root_id)
                return d
        else:
            # lbaas v1 -- one vthunder per tenant
            root_id = None
            tb = models.A10TenantBinding.find_by_tenant_id(tenant_id, db_session=db_session)
            if tb is not None:
                d = self.driver.config.get_device(tb.device_name, db_session=db_session)
                if d is None:
                    raise ex.InstanceMissing(
                        'A10 instance mapped to tenant %s is not present in db; '
                        'add it back to config or migrate loadbalancers' % tenant_id)
                return d

        # No? Then we need to create one.

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

        if root_id is not None:
            models.A10SLB.create_and_save(
                tenant_id=tenant_id,
                device_name=device_config['name'],
                loadbalancer_id=root_id,
                db_session=db_session)
        else:
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
