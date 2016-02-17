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

import abc
import six

import acos_client
from keystoneclient.auth.identity import generic as auth_plugin
from keystoneclient import session as keystone_session
from oslo_config import cfg

import a10_neutron_lbaas.a10_exceptions as a10_ex
import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.db.operations as db_operations
import a10_neutron_lbaas.instance_manager as a10_instance_manager


@six.add_metaclass(abc.ABCMeta)
class SchedulingHooks(object):
    """Interface for scheduling hooks"""

    @abc.abstractmethod
    def select_devices(self, a10_context, device_list, **kwargs):
        pass


class DevicePerTenant(SchedulingHooks):

    def __init__(self, underlying_scheduler):
        self.underlying_scheduler = underlying_scheduler

    def select_devices(self, a10_context, device_list, **kwargs):
        """Chooses the appliance a tenant is already on, or assigns it"""
        tenant_id = a10_context.tenant_id
        db_operations = a10_context.db_operations
        tenant = db_operations.get_tenant_appliance(tenant_id)
        if tenant is None:
            # Assign this tenant to an appliance
            devices = self.underlying_scheduler.select_devices(a10_context, device_list, **kwargs)

            try:
                device = next(devices.__iter__())
            except StopIteration:
                raise a10_ex.NoDevicesAvailableError("No devices are available for selection.")
            except Exception:
                raise

            # We need an appliance to save the a10 tenant appliance
            appliance = a10_context.inventory.device_appliance(device)

            # The underlying_scheduler might have assigned the tenant to an appliance
            tenant = db_operations.get_tenant_appliance(tenant_id)
            if tenant is None:
                tenant = models.default(
                    models.A10TenantAppliance,
                    tenant_id=tenant_id,
                    a10_appliance=appliance)
                db_operations.add(tenant)

        device = tenant.a10_appliance.device(a10_context)

        return [device]


class ExistingDevice(SchedulingHooks):
    """Uses an existing device. Prefers a device owned by the tenant"""

    def select_devices(self, a10_context, device_list, **kwargs):
        if any(device_list):
            tenant_id = a10_context.tenant_id

            device_dict = dict([
                (getattr(x.get('appliance'), 'id', None) or 'key-' + x.get('key'), x)
                for x in device_list])
            appliance_hash = acos_client.Hash(device_dict.keys())
            key = appliance_hash.get_server(tenant_id)
            return [device_dict[key]]

        return []


class TenantDevice(ExistingDevice):
    """Uses an existing device owned by the tenant"""

    def select_devices(self, a10_context, device_list, **kwargs):
        tenant_id = a10_context.tenant_id
        tenant_devices = filter(
            lambda x: getattr(x.get('appliance'), 'tenant_id', None) == tenant_id,
            device_list)

        return super(TenantDevice, self).select_devices(a10_context, tenant_devices, **kwargs)


class Fallback(SchedulingHooks):
    """Falls back across multiple schedulers.
    Only devices from a single scheduler are returned
    """

    def __init__(self, *underlying_schedulers):
        self.underlying_schedulers = underlying_schedulers

    def select_devices(self, a10_context, device_list, **kwargs):
        for underlying_scheduler in self.underlying_schedulers:
            any_devices = False
            devices = underlying_scheduler.select_devices(a10_context, device_list, **kwargs)
            for device in devices:
                yield device
                any_devices = True
            if any_devices:
                break


def existing_device_per_tenant(a10_driver):
    existing_device = Fallback(TenantDevice(), ExistingDevice())
    device_per_tenant = DevicePerTenant(existing_device)
    return device_per_tenant


class PlumbingHooksDevice(SchedulingHooks):
    """Uses only devices listed in the config file.
    Asks plumbing hooks to select_device

    Provided for backwards compatibility with systems that implemented custom plumbing hooks
    """

    def __init__(self, plumbing_hooks):
        self.plumbing_hooks = plumbing_hooks

    def select_devices(self, a10_context, device_list, **kwargs):
        device = self.plumbing_hooks.select_device(a10_context.tenant_id)
        return filter(lambda x: x.get('key', None) == device['key'], device_list)


def plumbing_hooks_device_per_tenant(plumbing_hooks):
    def f(a10_driver):
        plumbing_hooks_scheduler = PlumbingHooksDevice(plumbing_hooks)
        device_per_tenant = DevicePerTenant(plumbing_hooks_scheduler)
        return device_per_tenant
    return f


class LaunchDevice(SchedulingHooks):
    """Launches a default instance
    """

    def __init__(self, context_instance_manager=None):
        self.context_instance_manager = context_instance_manager or self.tenant_instance_manager

    def tenant_instance_manager(self, a10_context):
        tenant_id = a10_context.tenant_id
        auth_token = a10_context.openstack_context.auth_token

        auth_url = cfg.CONF.keystone_authtoken.auth_uri

        token = auth_plugin.Token(token=auth_token,
                                  tenant_id=tenant_id,
                                  auth_url=auth_url)
        session = keystone_session.Session(auth=token)

        instance_manager = a10_instance_manager.InstanceManager(tenant_id, session=session)
        return instance_manager

    def select_devices(self, a10_context, device_list, **kwargs):
        instance_manager = self.context_instance_manager(a10_context)

        try:
            device_config = instance_manager.create_default_instance()
        except a10_ex.FeatureNotConfiguredError:
            return []

        appliance = a10_context.inventory.device_appliance(device_config)
        device = appliance.device(a10_context)

        return [device]


def launch_device_per_tenant(a10_driver):
    existing_device = Fallback(TenantDevice(), LaunchDevice(), ExistingDevice())
    device_per_tenant = DevicePerTenant(existing_device)
    return device_per_tenant
