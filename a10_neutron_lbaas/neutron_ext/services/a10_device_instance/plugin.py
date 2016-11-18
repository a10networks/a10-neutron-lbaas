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

import a10_neutron_lbaas.a10_config as a10_config
from a10_neutron_lbaas.neutron_ext.common import constants
import a10_neutron_lbaas.neutron_ext.db.a10_device_instance as a10_device_instance
import a10_neutron_lbaas.vthunder.instance_manager as instance_manager
from a10_openstack_lib.resources import a10_device_instance as resources


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
        # Attempt to create instance using neutron context
        config = a10_config.A10Config()
        vth_config = config.get_vthunder_config()
        imgr = instance_manager.InstanceManager.from_config(config, context)
        # #TODO(mdurrant) This is in a constant, use it
        # Pass the member dict to avoid unnecessary transforms.

        dev_instance = a10_device_instance.get(resources.RESOURCE)

        instance = imgr.build_server_with_defaults(dev_instance, vth_config)
        instance = imgr.create_instance(instance)
        host_ip = instance.get("ip_address")
        nova_instance_id = instance.get("nova_instance_id")
        # things we don't know until the instance is created.
        dev_instance["host"] = host_ip
        dev_instance["nova_instance_id"] = nova_instance_id

        # If success, return the created DB record
        # Else, raise an exception because that's what we would do anyway
        return super(A10DeviceInstancePlugin, self).create_a10_device_instance(context,
                                                                               a10_device_instance)

    def get_a10_device_instance(self, context, id, fields=None):
        LOG.debug("A10DeviceInstancePlugin.get_a10_instance(): id=%s, fields=%s",
                  id, fields)
        return super(A10DeviceInstancePlugin, self).get_a10_device_instance(context,
                                                                            id,
                                                                            fields=fields)

    def update_a10_device_instance(self, context, id, a10_device_instance):
        LOG.debug(
            "A10DeviceInstancePlugin.update_a10_device_instance(): id=%s, instance=%s",
            id,
            a10_device_instance)

        return super(A10DeviceInstancePlugin, self).a10_device_instance(
            context,
            id,
            a10_device_instance)

    def delete_a10_device_instance(self, context, id):
        LOG.debug("A10DeviceInstancePlugin.delete(): id=%s", id)
        # Deleting the actual instance requires knowing the nova instance ID
        instance = super(A10DeviceInstancePlugin, self).get_a10_device_instance(context,
                                                                                id)
        nova_instance_id = instance.get("nova_instance_id")
        config = a10_config.A10Config()
        imgr = instance_manager.InstanceManager.from_config(config, context)
        imgr.delete_instance(nova_instance_id)

        return super(A10DeviceInstancePlugin, self).delete_a10_device_instance(context, id)
