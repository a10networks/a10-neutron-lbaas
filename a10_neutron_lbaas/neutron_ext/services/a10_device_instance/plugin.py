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
import a10_neutron_lbaas.neutron_ext.db.a10_device_instance as a10_device_instance

LOG = logging.getLogger(__name__)


class A10DeviceInstancePlugin(a10_device_instance.A10DeviceInstanceDbMixin):

    supported_extension_aliases = [constants.A10_DEVICE_INSTANCE_EXT]

    def get_a10_device_instances(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DeviceInstancePlugin.get_a10_instances(): filters=%s, fields=%s",
            filters,
            fields)
        return super(A10DeviceInstancePlugin, self).get_a10_device_instances(
            context, filters=filters, fields=fields)

    def create_a10_device_instance(self, context, a10_device_instance):
        LOG.debug("A10DeviceInstancePlugin.create(): a10_device_instance=%s", a10_device_instance)
        return super(A10DeviceInstancePlugin, self).create_a10_device_instance(context,
                                                                               a10_device_instance)

    def get_a10_device_instance(self, context, id, fields=None):
        LOG.debug("A10DeviceInstancePlugin.get_a10_instance(): id=%s, fields=%s",
                  id, fields)
        return super(A10DeviceInstancePlugin, self).get_a10_device_instance(context,
                                                                            id,
                                                                            fields=fields)

    # def update_a10_device_instance(self, context, id, a10_device_instance):
    #     LOG.debug(
    #         "A10DeviceInstancePlugin.update_a10_device_instance(): id=%s, instance=%s",
    #         id,
    #         a10_device_instance)
    #     return super(A10DeviceInstancePlugin, self).a10_device_instance(
    #         context,
    #         id,
    #         a10_device_instance)

    # def delete_a10_device_instance(self, context, id):
    #     LOG.debug("A10DeviceInstancePlugin.delete(): id=%s", id)
    #     return super(A10DeviceInstancePlugin, self).delete_a10_device_instance(context, id)
