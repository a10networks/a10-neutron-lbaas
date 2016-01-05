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

from neutronclient.common import extension
from neutronclient.neutron import v2_0 as neutronV20

from a10_neutron_lbaas_client.resources import a10_appliance

_NEUTRON_OPTIONS = ['id', 'tenant_id']


def _arg_name(name):
    """--shish-kabob it"""
    return '--%s' % name.replace('_', '-')


def _add_known_arguments(parser, required, where):
    attributes = a10_appliance.RESOURCE_ATTRIBUTE_MAP[a10_appliance.RESOURCES]
    for name in required:
        parser.add_argument(name)
    for name, attr in attributes.items():
        if name in required or name in _NEUTRON_OPTIONS or not where(attr):
            continue
        parser.add_argument(_arg_name(name), dest=name)


def _args2body(parsed_args):
    attributes = a10_appliance.RESOURCE_ATTRIBUTE_MAP[a10_appliance.RESOURCES]
    body = {}
    neutronV20.update_dict(parsed_args, body, [a for a in attributes if a != 'id'])
    return {a10_appliance.RESOURCE: body}


class a10_applianceExtension(extension.NeutronClientExtension):
    """Define required variables for resource operations."""

    resource = a10_appliance.RESOURCE
    resource_plural = a10_appliance.RESOURCES

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class Lista10_appliance(extension.ClientExtensionList, a10_applianceExtension):
    """List A10 appliances"""

    shell_command = 'a10-appliance-list'

    list_columns = ['id', 'name', 'host', 'api_version', 'description']
    pagination_support = True
    sorting_support = True


class Createa10_appliance(extension.ClientExtensionCreate, a10_applianceExtension):
    """Create A10 appliance"""

    shell_command = 'a10-appliance-create'

    list_columns = ['id', 'name', 'host', 'api_version', 'description']

    def add_known_arguments(self, parser):
        _add_known_arguments(
            parser,
            ['host', 'api_version', 'username', 'password'],
            lambda attr: attr.get('allow_post'))

    def args2body(self, parsed_args):
        return _args2body(parsed_args)


class Updatea10_appliance(extension.ClientExtensionUpdate, a10_applianceExtension):
    """Update A10 appliance"""

    shell_command = 'a10-appliance-update'

    list_columns = ['id', 'name', 'host', 'api_version', 'description']

    def add_known_arguments(self, parser):
        _add_known_arguments(
            parser,
            [],
            lambda attr: attr.get('allow_put'))

    def args2body(self, parsed_args):
        return _args2body(parsed_args)


class Deletea10_appliance(extension.ClientExtensionDelete, a10_applianceExtension):
    """Delete A10 appliance"""

    shell_command = 'a10-appliance-delete'


class Showa10_appliance(extension.ClientExtensionShow, a10_applianceExtension):
    """Show A10 appliance"""

    shell_command = 'a10-appliance-show'
