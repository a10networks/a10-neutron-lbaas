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

# import abc
# import six

# import acos_client
# from keystoneclient.auth.identity import generic as auth_plugin
# from keystoneclient import session as keystone_session
# from oslo_config import cfg

# import a10_neutron_lbaas.a10_exceptions as a10_ex
# import a10_neutron_lbaas.db.models as models
# import a10_neutron_lbaas.instance_manager as a10_instance_manager

import base


class ServiceTenant(base.BaseSchedulerFilter):

    def __init__(self, driver, devices):
        super(ServiceTenant, self).__init__(driver, devices)
        self.instance_manager = instance_manager.Foo(todo)

    def select_device(self, a10_context=None, devices, tenant_id, lbaas_obj=None):
        if not self.driver.config.get('use_database'):
            raise MakesNoSenseError()

        # TODO(dougwig) -- this all belongs in instance_manager
        # service_tenant_id = self.driver.config.get_vthunder('service_tenant_id')
        # creds = todo_same

        # auth_url = todo_without_CFG_dangit
        # token = auth_plugin.Token(token=auth_token_NOPE_NOPE,
        #                           tenant_id=service_tenant_id,
        #                           auth_url=auth_url)
        # session = keystone_session.Session(auth=token)

        try:
            device_config = instance_manager.create_default_instance()
        except a10_ex.FeatureNotConfiguredError:
            return []

        # appliance = a10_context.inventory.device_appliance(device_config)
        # device = appliance.device(a10_context)

        if that worked, save a db model

        return [device_config]
