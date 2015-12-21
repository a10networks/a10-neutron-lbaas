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

import neutron.db.common_db_mixin as common_db_mixin
from oslo_log import log as logging

import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.neutron_ext.extensions.a10Image as a10Image


LOG = logging.getLogger(__name__)


class A10ImageDbMixin(common_db_mixin.CommonDbMixin, a10Image.A10ImagePluginBase):

    def _get_a10_image(self, context, a10_image_id):
        try:
            return self._get_by_id(context, models.A10Image, a10_image_id)
        except Exception:
            raise a10Image.A10ImageNotFoundError(a10_image_id)

    def _make_a10_image_dict(self, a10_image_db, fields=None):
        res = {'id': a10_image_db['id'],
               'name': a10_image_db['name'],
               'tenant_id': a10_image_db['tenant_id'],
               'description': a10_image_db['description'],
               'image_id': a10_image_db['image_id'],
               'api_version': a10_image_db['api_version'],
               'username': a10_image_db['username'],
               'password': a10_image_db['password']}
        return self._fields(res, fields)

    def _ensure_a10_image_not_in_use(self, context, a10_image_id):
        pass

    def create_a10_image(self, context, a10_image):
        body = a10_image[a10Image.A10_IMAGE_RESOURCE]
        with context.session.begin(subtransactions=True):
            image_record = models.A10Image(
                id=models.uuid_str(),
                name=body['name'],
                description=body['description'],
                image_id=body['image_id'],
                api_version=body['api_version'],
                username=body['username'],
                password=body['password'],
                tenant_id=context.tenant_id)
            context.session.add(image_record)

        return self._make_a10_image_dict(image_record)

    def update_a10_image(self, context, a10_image_id, a10_image):
        data = a10_image[a10Image.A10_IMAGE_RESOURCE]
        with context.session.begin(subtransactions=True):
            a10_image_db = self._get_a10_image(context, a10_image_id)
            a10_image_db.update(data)

        return self._make_a10_image_dict(a10_image_db)

    def delete_a10_image(self, context, a10_image_id):
        with context.session.begin(subtransactions=True):
            self._ensure_a10_image_not_in_use(context, a10_image_id)
            LOG.debug("A10ImageDbMixin:delete_a10_image(): a10_image_id={0}".format(
                a10_image_id))
            image = self._get_a10_image(context, a10_image_id)
            context.session.delete(image)

    def get_a10_image(self, context, a10_image_id, fields=None):
        image = self._get_a10_image(context, a10_image_id)
        return self._make_a10_image_dict(image, fields)

    def get_a10_images(self, context, filters=None, fields=None,
                       sorts=None, limit=None, marker=None,
                       page_reverse=False):
        LOG.debug("A10ImageDbMixin:get_a10_images() tenant_id=%s" % context.tenant_id)
        return self._get_collection(context, models.A10Image,
                                    self._make_a10_image_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)
