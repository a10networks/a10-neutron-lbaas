# Copyright 2015-2017,  A10 Networks

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

import itertools
from oslo_log import log as logging

import a10_neutron_lbaas.a10_config as a10_config
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.common import resources as common_resources

import a10_neutron_lbaas.neutron_ext.db.a10_device as a10_device
import a10_neutron_lbaas.vthunder.instance_manager as instance_manager
from a10_openstack_lib.resources import a10_device as resources

LOG = logging.getLogger(__name__)

# api, vthunder, instance, and db keys
_API = 0
_VTHUNDER_CONFIG = 1
_VTHUNDER = 2
_DB = 3

_vthunder_mappings = [("id", None, None, "id"),
                      ("tenant_id", None, None, "tenant_id"),
                      ("tenant_id", None, None, "project_id"),
                      ("project_id", None, None, "tenant_id"),
                      ("project_id", None, None, "project_id"),
                      ("name", None, None, "name"),
                      ("description", None, None, "description"),
                      ("host", None, "ip_address", "host"),
                      ("username", "username", None, "username"),
                      ("password", "password", None, "password"),
                      ("api_version", "api_version", None, "api_version"),
                      ("protocol", "protocol", None, "protocol"),
                      ("port", "port", None, "port"),
                      ("nova_instance_id", None, "nova_instance_id", "nova_instance_id"),
                      (None, "autosnat", None, "autosnat"),
                      (None, "v_method", None, "v_method"),
                      (None, "shared_partition", None, "shared_partition"),
                      (None, "use_float", None, "use_float"),
                      (None, "default_virtual_server_vrid", None, "default_virtual_server_vrid"),
                      (None, "ipinip", None, "ipinip"),
                      (None, "write_memory", None, "write_memory"),
                      ("management_network", "vthunder_management_network", None, None),
                      ("data_networks", "vthunder_data_networks", None, None),
                      ("image", "glance_image", None, None),
                      ("flavor", "nova_flavor", None, None)]

def _convert(source, from_type, to_type):
    result = {}
    for mapping in _vthunder_mappings:
        source_key = mapping[from_type]
        if source_key is None or source_key not in source:
            continue

        dest_key = mapping[to_type]
        if dest_key is None:
            continue

        result[dest_key] = source[source_key]

    return result


def _make_api_dict(db_record):
    return _convert(db_record, _DB, _API)


class A10DevicePlugin(a10_device.A10DeviceDbMixin):

    supported_extension_aliases = [constants.A10_DEVICE_EXT]

    def get_a10_vthunders(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DevicePlugin.get_a10_vthunders(): filters=%s, fields=%s",
            filters,
            fields)

        db_instances = super(A10DevicePlugin, self).get_a10_devices(
            context, filters=filters, fields=fields)

        cnt = 0
        while cnt < len(db_instances):
            if not db_instances[cnt].get("nova_instance_id"):
                del db_instances[cnt]
                cnt -= 1
            cnt += 1

        return map(_make_api_dict, db_instances)

    
    def create_a10_vthunder(self, context, a10_vthunder):
        """Attempt to create vthunder using neutron context"""
        LOG.debug("A10DevicePlugin.create(): vthunder=%s", a10_vthunder)

        config = a10_config.A10Config()
        vthunder_defaults = config.get_vthunder_config()
        imgr = instance_manager.InstanceManager.from_config(config, context)

        dev_instance = common_resources.remove_attributes_not_specified(
            a10_vthunder.get(resources.VTHUNDER))

        # Create the instance with specified defaults.
        vthunder_config = vthunder_defaults.copy()
        vthunder_config.update(_convert(dev_instance, _API, _VTHUNDER_CONFIG))
        instance = imgr.create_device_instance(vthunder_config, dev_instance.get("name"))

        db_record = {}
        db_record.update(_convert(vthunder_config, _VTHUNDER_CONFIG, _DB))
        db_record.update(_convert(dev_instance, _API, _DB))
        db_record.update(_convert(instance, _VTHUNDER, _DB))

        # If success, return the created DB record
        # Else, raise an exception because that's what we would do anyway
        db_instance = super(A10DevicePlugin, self).create_a10_device(
            context, {resources.VTHUNDER: db_record}, resources.VTHUNDER)

        vthunder_dict = {'extra_resources': db_instance['extra_resources']}
        vthunder_dict.update(_make_api_dict(db_instance))

        return vthunder_dict 

    def get_a10_vthunder(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_a10_vthunder(): id=%s, fields=%s",
                  id, fields)
        db_instance = super(A10DevicePlugin, self).get_a10_device(
            context, id, fields=fields)

        if not db_instance.get("nova_instance_id"):
            return {}

        extra_resources = db_instance['extra_resources']
        del db_instance['extra_resources']

        return _make_api_dict(db_instance), extra_resources

    def update_a10_vthunder(self, context, id, vthunder):
        LOG.debug(
            "A10DevicePlugin.update_vthunder(): id=%s, vthunder=%s",
            id,
            vthunder)

        db_instance = super(A10DevicePlugin, self).update_a10_device(
            context, id, vthunder, 'vthunder')

        return _make_api_dict(db_instance)

    def delete_a10_vthunder(self, context, id):
        LOG.debug("A10DevicePlugin.a10_vthunder_delete(): id=%s", id)
        # Deleting the actual instance requires knowing the nova instance ID
        vthunder = super(A10DevicePlugin, self).get_a10_device(context, id)

        nova_instance_id = vthunder.get("nova_instance_id")
        config = a10_config.A10Config()
        imgr = instance_manager.InstanceManager.from_config(config, context)
        imgr.delete_instance(nova_instance_id)

        return super(A10DevicePlugin, self).delete_a10_device(context, id)

    def get_a10_devices(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DevicePlugin.get_a10_devices(): filters=%s, fields=%s",
            filters,
            fields)

        db_instances = super(A10DevicePlugin, self).get_a10_devices(
            context, filters=filters, fields=fields)

        cnt = 0
        while cnt < len(db_instances):
            if db_instances[cnt].get("nova_instance_id"):
                del db_instances[cnt]
                cnt -= 1
            cnt += 1

        return db_instances

    def create_a10_device(self, context, a10_device):
        """Attempt to create vthunder using neutron context"""
        LOG.debug("A10DevicePlugin.create_a10_device(): device=%s", a10_device)

        # Else, raise an exception because that's what we would do anyway
        return super(A10DevicePlugin, self).create_a10_device(context, a10_device)

    def get_a10_device(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_a10_device(): id=%s, fields=%s",
                  id, fields)
        db_instance = super(A10DevicePlugin, self).get_a10_device(
            context, id, fields=fields)
        if db_instance.get("nova_instance_id"):
            return {}

        extra_resources = db_instance['extra_resources']
        del db_instance['extra_resources']

        return db_instance, extra_resources

    def update_a10_device(self, context, id, device):
        LOG.debug(
            "A10DevicePlugin.update_a10_device(): id=%s, device=%s",
            id,
            device)

        return super(A10DevicePlugin, self).update_a10_device(
            context, id, device)

    def delete_a10_device(self, context, id):
        LOG.debug("A10DevicePlugin.a10_device_delete(): id=%s", id)
        return super(A10DevicePlugin, self).delete_a10_device(context, id)

    def get_a10_device_keys(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DevicePlugin.get_a10_devices(): filters=%s, fields=%s",
            filters,
            fields)

        return super(A10DevicePlugin, self).get_a10_device_keys(
            context, filters=filters, fields=fields)

    def create_a10_device_key(self, context, a10_device_key):
        """Attempt to create vthunder using neutron context"""
        LOG.debug("A10DevicePlugin.create_a10_device(): device=%s", a10_device_key)

        # Else, raise an exception because that's what we would do anyway
        return super(A10DevicePlugin, self).create_a10_device_key(context, a10_device_key)

    def get_a10_device_key(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_a10_device_key(): id=%s, fields=%s",
                  id, fields)

        db_instance = super(A10DevicePlugin, self).get_a10_device_key(
            context, id, fields=fields)

        return db_instance

    def update_a10_device_key(self, context, id, key):
        LOG.debug(
            "A10DevicePlugin.update_a10_device_key(): id=%s, device=%s",
            id,
            key)

        return super(A10DevicePlugin, self).update_a10_device_key(
            context, id, key)

    def delete_a10_device_key(self, context, id):
        LOG.debug("A10DevicePlugin.a10_device_delete_key(): id=%s", id)
        return super(A10DevicePlugin, self).delete_a10_device_key(context, id)

    def get_a10_device_values(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DevicePlugin.get_a10_device_values(): filters=%s, fields=%s",
            filters,
            fields)

        return super(A10DevicePlugin, self).get_a10_device_values(
            context, filters=filters, fields=fields)

    def create_a10_device_value(self, context, a10_device_value):
        """Attempt to create vthunder using neutron context"""
        LOG.debug("A10DevicePlugin.create_a10_device_value(): device=%s", a10_device_value)
        # Else, raise an exception because that's what we would do anyway
        return super(A10DevicePlugin, self).create_a10_device_value(context, a10_device_value)

    def get_a10_device_value(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_a10_device_value(): id=%s, fields=%s",
                  id, fields)

        db_instance = super(A10DevicePlugin, self).get_a10_device_value(
            context, id, fields=fields)

        return db_instance

    def update_a10_device_value(self, context, id, value):
        LOG.debug(
            "A10DevicePlugin.update_a10_device_value(): id=%s, device=%s",
            id,
            value)

        return super(A10DevicePlugin, self).update_a10_device_value(
            context, id, value)

    def delete_a10_device_value(self, context, id):
        LOG.debug("A10DevicePlugin.a10_device_delete_value(): id=%s", id)
        return super(A10DevicePlugin, self).delete_a10_device_value(context, id)


