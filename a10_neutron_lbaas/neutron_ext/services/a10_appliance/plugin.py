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

import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.extensions.a10_appliance as a10_appliance


class A10AppliancePlugin(a10_appliance.A10AppliancePluginBase):

    supported_extension_aliases = [constants.A10_APPLIANCE_EXT]

    def __init__(self):
        super(A10AppliancePlugin, self).__init__()

    def get_a10_appliances(self, context, filters=None, fields=None):
        LOG.debug("A10AppliancePlugin.get_a10_appliances(): filters=%s, fields=%s", filters, fields)
        raise NotSupportedException()

    def create_a10_appliance(self, context, a10_appliance):
        LOG.debug("A10AppliancePlugin.create(): context=%s, id=%s", context, id)
        raise NotSupportedException()

    def get_a10_appliance(self, context, id, fields=None):
        LOG.debug("A10AppliancePlugin.get_a10_appliance(): context=%s, id=%s", context, id)
        raise NotSupportedException()

    def update_a10_appliance(self, context, a10_appliance_id, a10_appliance):
        LOG.debug("A10AppliancePlugin.update_a10_appliance(): context=%s, cert=%s", context,
                  a10_appliance)
        raise NotSupportedException()

    def delete_a10_appliance(self, context, id):
        LOG.debug("A10AppliancePlugin.delete(): context=%s, id=%s", context, id)
        raise NotSupportedException()
