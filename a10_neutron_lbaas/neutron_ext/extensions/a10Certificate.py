# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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
import logging
import six

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.api.v2 import resource_helper
from neutron.services import service_base

from a10_neutron_lbaas.neutron_ext.common import constants
import a10_neutron_lbaas.neutron_ext.common.resources as resources
from a10_openstack_lib.resources import a10_certificate


RESOURCE_ATTRIBUTE_MAP = resources.apply_template(
    a10_certificate.RESOURCE_ATTRIBUTE_MAP, attributes)

attributes.validators.update(resources.apply_template(a10_certificate.VALIDATORS,
                                                      attributes.validators))

LOG = logging.getLogger(__name__)


class A10Certificate(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "A10 LBaaS Certificate Management"

    @classmethod
    def get_alias(cls):
        return constants.A10_CERTIFICATE_EXT

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/neutron/a10-certificates/api/v1.0"

    @classmethod
    def get_updated(cls):
        return "2016-06-19T16:20:13-07:00"

    @classmethod
    def get_description(cls):
        return ("A10 Networks SSL Certificiate Management")

    @classmethod
    def get_resources(cls):
        """Returns external resources."""
        my_plurals = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        attributes.PLURALS.update(my_plurals)
        attr_map = RESOURCE_ATTRIBUTE_MAP
        ext_resources = resource_helper.build_resource_info(my_plurals,
                                                            attr_map,
                                                            constants.A10_CERTIFICATE)

        return ext_resources

    def update_attributes_map(self, attributes):
        super(A10Certificate, self).update_attributes_map(
            attributes,
            extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


@six.add_metaclass(abc.ABCMeta)
class A10CertificatePluginBase(service_base.ServicePluginBase):

    def get_plugin_name(self):
        return constants.A10_CERTIFICATE

    def get_plugin_description(self):
        return constants.A10_CERTIFICATE

    def get_plugin_type(self):
        return constants.A10_CERTIFICATE

    def __init__(self):
        super(A10CertificatePluginBase, self).__init__()

    @abc.abstractmethod
    def get_a10_certificates(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_certificate(self, context, a10_certificate):
        pass

    @abc.abstractmethod
    def get_a10_certificate(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def update_a10_certificate(self, context, certificate):
        pass

    @abc.abstractmethod
    def delete_a10_certificate(self, context, id):
        pass

    @abc.abstractmethod
    def get_a10_certificate_listener_bindings(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_certificate_listener_binding(self, context, a10_certificate_binding):
        pass

    @abc.abstractmethod
    def get_a10_certificate_listener_binding(self, context, id):
        pass

    @abc.abstractmethod
    def delete_a10_certificate_listener_binding(self, context, id):
        pass
