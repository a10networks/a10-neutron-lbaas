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

import mock

import a10_neutron_lbaas.tests.db.test_base as test_base

import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.db.a10_image as a10_image
import a10_neutron_lbaas.neutron_ext.extensions.a10Image as a10Image


class TestA10ImageDbMixin(test_base.UnitTestBase):

    def setUp(self):
        super(TestA10ImageDbMixin, self).setUp()
        self.plugin = a10_image.A10ImageDbMixin()

    def context(self):
        session = self.open_session()
        context = mock.MagicMock(session=session, tenant_id='fake-tenant-id')
        return context

    def fake_image(self):
        return {
            'name': 'fake-name',
            'description': 'fake-description',
            'image_id': 'fake-image-id',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password'
        }

    def envelope(self, body):
        return {a10Image.A10_IMAGE_RESOURCE: body}

    def test_create_a10_image(self):
        image = self.fake_image()
        context = self.context()
        result = self.plugin.create_a10_image(context, self.envelope(image))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        expected = image.copy()
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id
            })
        self.assertEqual(expected, result)

    def test_get_a10_image(self):
        image = self.fake_image()
        create_context = self.context()
        create_result = self.plugin.create_a10_image(create_context, self.envelope(image))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_image(context, create_result['id'])

        self.assertEqual(create_result, result)

    def test_get_a10_image_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Image.A10ImageNotFoundError,
            self.plugin.get_a10_image,
            context,
            'fake-image-id')

    def test_get_a10_images(self):
        image = self.fake_image()
        create_context = self.context()
        create_result = self.plugin.create_a10_image(create_context, self.envelope(image))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_images(context)

        self.assertEqual([create_result], result)

    def test_delete_a10_image(self):
        image = self.fake_image()
        create_context = self.context()
        create_result = self.plugin.create_a10_image(create_context, self.envelope(image))
        create_context.session.commit()

        context = self.context()
        self.plugin.delete_a10_image(context, create_result['id'])
        context.session.commit()

        get_context = self.context()
        self.assertRaises(
            a10Image.A10ImageNotFoundError,
            self.plugin.get_a10_image,
            get_context,
            create_result['id'])

    def test_delete_a10_image_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Image.A10ImageNotFoundError,
            self.plugin.delete_a10_image,
            context,
            'fake-image-id')

    def test_update_a10_image(self):
        image = self.fake_image()
        create_context = self.context()
        create_result = self.plugin.create_a10_image(create_context, self.envelope(image))
        create_context.session.commit()

        change = {
            'api_version': 'other-version'
        }
        expected = create_result.copy()
        expected.update(change)

        context = self.context()
        result = self.plugin.update_a10_image(context,
                                              create_result['id'],
                                              self.envelope(change))
        context.session.commit()

        self.assertEqual(expected, result)

        get_context = self.context()
        get_result = self.plugin.get_a10_image(get_context, create_result['id'])

        self.assertEqual(expected, get_result)

    def test_update_a10_image_not_found(self):
        change = {
            'api_version': 'other-version'
        }
        context = self.context()
        self.assertRaises(
            a10Image.A10ImageNotFoundError,
            self.plugin.update_a10_image,
            context,
            'fake-image-id', self.envelope(change))

    def test_get_plugin_name(self):
        self.assertIsNot(self.plugin.get_plugin_name(), None)

    def test_get_plugin_description(self):
        self.assertIsNot(self.plugin.get_plugin_description(), None)

    def test_get_plugin_type(self):
        self.assertEqual(self.plugin.get_plugin_type(), constants.A10_IMAGE)
