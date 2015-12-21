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
import a10_neutron_lbaas.neutron_ext.db.a10_image as a10_image

LOG = logging.getLogger(__name__)


class A10ImagePlugin(a10_image.A10ImageDbMixin):

    supported_extension_aliases = [constants.A10_IMAGE_EXT]

    def get_a10_images(self, context, filters=None, fields=None):
        LOG.debug(
            "A10ImagePlugin.get_a10_images(): filters=%s, fields=%s",
            filters,
            fields)
        return super(A10ImagePlugin, self).get_a10_images(
            context, filters=filters, fields=fields)

    def create_a10_image(self, context, a10_image):
        LOG.debug("A10ImagePlugin.create(): a10_image=%s", a10_image)
        return super(A10ImagePlugin, self).create_a10_image(context, a10_image)

    def get_a10_image(self, context, id, fields=None):
        LOG.debug("A10ImagePlugin.get_a10_image(): id=%s, fields=%s", context, id, fields)
        return super(A10ImagePlugin, self).get_a10_image(context, id, fields=fields)

    def update_a10_image(self, context, a10_image_id, a10_image):
        LOG.debug(
            "A10ImagePlugin.update_a10_image(): a10_image_id=%s, a10_image=%s",
            a10_image_id,
            a10_image)
        return super(A10ImagePlugin, self).update_a10_image(
            context,
            a10_image_id,
            a10_image)

    def delete_a10_image(self, context, id):
        LOG.debug("A10ImagePlugin.delete(): id=%s", id)
        return super(A10ImagePlugin, self).delete_a10_image(context, id)
