# Copyright (C) 2017, A10 Networks Inc. All rights reserved.
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
#    under the License.from oslo_log.helpers import logging as logging
import logging

from neutron_lbaas.services.loadbalancer import plugin


LOG = logging.getLogger(__name__)

class A10ConfigPlugin(object):

    supported_extension_aliases = [constants.A10_DEVICE_CONFIG_EXT]

    def get_a10_device_config(self, context, filters=None, fields=None):
        LOG.debug(
            "A10ConfigPlugin.get_a10_config(): filters=%s, fields=%s", 
            filters,
            fields)

        db_config = super(A10ConfigPlugin, self).get_a10_device_config(
            context, filsters=filters, fields=fields)

        return db_config

    def create_a10_device_config(self, context, a10_device_config):
        LOG.debug(
            "A10ConfigPlugin.create(): a10_device_config=%s", a10_device_config)

        config = a10_config.A10Config() if not a10_device_config else a10_device_config

        db_record = {}
        db_record.update(_convert(config, _DEVICE_CONFIG, _DB))

        return super(A10DeviceConfigPlugin, self).create_a10_device_config(
            context, {resources.RESOURCE: db_record})


    def update_a10_device_config(self, context, a10_device_config):
        LOG.debug("A10DeviceConfigPLugin.update_device_config()")

        return super(A10DeviceConfigPLugin, self).update_a10_config(
            context,
            a10_device_config)

    def delete_a10_device_config(self, context):
        LOG.debug("A10DeviceInstancePlugin.delete()")

        return super(A10DeviceConfigPlugin, self).delete_a10_device_config(context)
