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

import neutronclient.common.extension as extension
import neutronclient.neutron.v2_0 as neutronV20

import a10_neutron_lbaas.neutron_ext.extensions.a10Image as a10Image


_NEUTRON_OPTIONS = ['id', 'tenant_id']


def _arg_name(name):
    """--shish-kabob it"""
    return '--%s' % name.replace('_', '-')


def _add_known_arguments(parser, required, where):
    attributes = a10Image.RESOURCE_ATTRIBUTE_MAP[a10Image.A10_IMAGE_RESOURCES]
    for name in required:
        parser.add_argument(name)
    for name, attr in attributes.items():
        if name in required or name in _NEUTRON_OPTIONS or not where(attr):
            continue
        parser.add_argument(_arg_name(name), dest=name)


def _args2body(parsed_args):
    attributes = a10Image.RESOURCE_ATTRIBUTE_MAP[a10Image.A10_IMAGE_RESOURCES]
    body = {}
    neutronV20.update_dict(parsed_args, body, [a for a in attributes if a != 'id'])
    return {a10Image.A10_IMAGE_RESOURCE: body}


class A10ImageExtension(extension.NeutronClientExtension):
    """Define required variables for resource operations."""

    resource = a10Image.A10_IMAGE_RESOURCE
    resource_plural = a10Image.A10_IMAGE_RESOURCES

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class ListA10Image(extension.ClientExtensionList, A10ImageExtension):
    """List A10 images"""

    shell_command = 'a10-image-list'

    list_columns = ['id', 'name', 'image_id', 'api_version', 'description']
    pagination_support = True
    sorting_support = True


class CreateA10Image(extension.ClientExtensionCreate, A10ImageExtension):
    """Create A10 image"""

    shell_command = 'a10-image-create'

    list_columns = ['id', 'name', 'image_id', 'api_version', 'description']

    def add_known_arguments(self, parser):
        _add_known_arguments(
            parser,
            ['image_id', 'api_version', 'username', 'password'],
            lambda attr: attr.get('allow_post'))

    def args2body(self, parsed_args):
        return _args2body(parsed_args)


class UpdateA10Image(extension.ClientExtensionUpdate, A10ImageExtension):
    """Update A10 image"""

    shell_command = 'a10-image-update'

    list_columns = ['id', 'name', 'image_id', 'api_version', 'description']

    def add_known_arguments(self, parser):
        _add_known_arguments(
            parser,
            [],
            lambda attr: attr.get('allow_put'))

    def args2body(self, parsed_args):
        return _args2body(parsed_args)


class DeleteA10Image(extension.ClientExtensionDelete, A10ImageExtension):
    """Delete A10 image"""

    shell_command = 'a10-image-delete'


class ShowA10Image(extension.ClientExtensionShow, A10ImageExtension):
    """Show A10 image"""

    shell_command = 'a10-image-show'
