
import abc
import six

import acos_client
from keystoneclient.auth.identity import generic as auth_plugin
from keystoneclient import session as keystone_session
from oslo_config import cfg

import a10_neutron_lbaas.a10_exceptions as a10_ex
import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.instance_manager as a10_instance_manager



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
