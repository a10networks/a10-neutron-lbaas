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

from oslo_log import log as logging

import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.db.a10_appliance as a10_appliance

LOG = logging.getLogger(__name__)


class A10AppliancePlugin(a10_appliance.A10ApplianceDbMixin):

    supported_extension_aliases = [constants.A10_APPLIANCE_EXT]

    def get_a10_appliances(self, context, filters=None, fields=None):
        LOG.debug(
            "A10AppliancePlugin.get_a10_appliances(): filters=%s, fields=%s",
            filters,
            fields)
        return super(A10AppliancePlugin, self).get_a10_appliances(
            context, filters=filters, fields=fields)

    def create_a10_appliance(self, context, a10_appliance):
        LOG.debug("A10AppliancePlugin.create(): a10_appliance=%s", a10_appliance)
        return super(A10AppliancePlugin, self).create_a10_appliance(context, a10_appliance)

    def get_a10_appliance(self, context, id, fields=None):
        LOG.debug("A10AppliancePlugin.get_a10_appliance(): id=%s, fields=%s", context, id, fields)
        return super(A10AppliancePlugin, self).get_a10_appliance(context, id, fields=fields)

    def update_a10_appliance(self, context, a10_appliance_id, a10_appliance):
        LOG.debug(
            "A10AppliancePlugin.update_a10_appliance(): a10_appliance_id=%s, a10_appliance=%s",
            a10_appliance_id,
            a10_appliance)
        return super(A10AppliancePlugin, self).update_a10_appliance(
            context,
            a10_appliance_id,
            a10_appliance)

    def delete_a10_appliance(self, context, id):
        LOG.debug("A10AppliancePlugin.delete(): id=%s", id)
        return super(A10AppliancePlugin, self).delete_a10_appliance(context, id)
