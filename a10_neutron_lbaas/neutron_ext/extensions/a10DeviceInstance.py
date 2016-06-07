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
#    under the License.

import abc
import six

import a10_openstack_lib.resources.a10_device_instance as a10_device_instance
from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.api.v2 import resource_helper
from neutron.common import exceptions
from neutron.services import service_base

import a10_neutron_lbaas.neutron_ext.common.constants as constants
from a10_neutron_lbaas.neutron_ext.common import resources

RESOURCE_ATTRIBUTE_MAP = resources.apply_template(a10_device_instance.RESOURCE_ATTRIBUTE_MAP,
                                                  attributes)


# TODO(rename this to *Extension to avoid config file confusion)
class A10DeviceInstance(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "A10 Device Instances"

    @classmethod
    def get_alias(cls):
        return constants.A10_DEVICE_INSTANCE_EXT

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/neutron/a10_device_instance/api/v1.0"

    @classmethod
    def get_updated(cls):
        return "2015-11-18T16:17:00-07:00"

    @classmethod
    def get_description(cls):
        return ("A10 Device Instances")

    @classmethod
    def get_resources(cls):
        """Returns external resources."""
        my_plurals = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        attributes.PLURALS.update(my_plurals)
        attr_map = RESOURCE_ATTRIBUTE_MAP
        resources = resource_helper.build_resource_info(my_plurals,
                                                        attr_map,
                                                        constants.A10_DEVICE_INSTANCE)

        return resources

    def update_attributes_map(self, attributes):
        super(A10DeviceInstance, self).update_attributes_map(
            attributes,
            extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


class A10DeviceInstanceNotFoundError(exceptions.NotFound):
    def __init__(self, a10_device_instance_id):
        self.msg = _("A10 Device Instance {} could not be found.")
        super(A10DeviceInstanceNotFoundError, self).__init__()


class A10DeviceInstanceInUseError(exceptions.InUse):
    def __init__(self, a10_device_instance_id):
        self.message = _("A10 Device Instance is in use and cannot be deleted.")
        self.msg = self.message
        super(A10DeviceInstanceInUseError, self).__init__()


@six.add_metaclass(abc.ABCMeta)
class A10DeviceInstancePluginBase(service_base.ServicePluginBase):

    def get_plugin_name(self):
        return constants.A10_DEVICE_INSTANCE

    def get_plugin_description(self):
        return constants.A10_DEVICE_INSTANCE

    def get_plugin_type(self):
        return constants.A10_DEVICE_INSTANCE

    def __init__(self):
        super(A10DeviceInstancePluginBase, self).__init__()

    @abc.abstractmethod
    def get_a10_device_instances(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_device_instance(self, context, device_instance):
        pass

    @abc.abstractmethod
    def get_a10_device_instance(self, context, id, fields=None):
        pass
