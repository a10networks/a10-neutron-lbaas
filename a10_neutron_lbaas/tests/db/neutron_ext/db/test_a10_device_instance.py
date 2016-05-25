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

import mock

import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.tests.db.test_base as test_base

import a10_neutron_lbaas.neutron_ext.common.constants as constants
import a10_neutron_lbaas.neutron_ext.db.a10_appliance as a10_appliance
import a10_neutron_lbaas.neutron_ext.extensions.a10Appliance as a10Appliance
from a10_neutronclient.resources import a10_appliance as a10_appliance_resources


class TestA10ApplianceDbMixin(test_base.UnitTestBase):

    def setUp(self):
        super(TestA10ApplianceDbMixin, self).setUp()
        self.plugin = a10_appliance.A10ApplianceDbMixin()

    def context(self):
        session = self.open_session()
        context = mock.MagicMock(session=session, tenant_id='fake-tenant-id')
        return context

    def fake_appliance(self):
        return {
            'name': 'fake-name',
            'description': 'fake-description',
            'host': 'fake-host',
            'api_version': 'fake-version',
            'username': 'fake-username',
            'password': 'fake-password',
            'nova_instance_id': None
        }

    def fake_appliance_options(self):
        return {
            'protocol': 'http',
            'port': 12345
        }

    def default_options(self):
        return {
            'protocol': 'https',
            'port': 443
        }

    def envelope(self, body):
        return {a10_appliance_resources.RESOURCE: body}

    def test_create_a10_appliance(self):
        appliance = self.fake_appliance()
        context = self.context()
        result = self.plugin.create_a10_appliance(context, self.envelope(appliance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        expected = self.default_options()
        expected.update(appliance)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id
            })
        self.assertEqual(expected, result)

    def test_create_a10_appliance_options(self):
        appliance = self.fake_appliance()
        appliance.update(self.fake_appliance_options())
        context = self.context()
        result = self.plugin.create_a10_appliance(context, self.envelope(appliance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        expected = appliance.copy()
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
            })
        self.assertEqual(expected, result)

    def test_create_a10_appliance_default_port(self):
        appliance = self.fake_appliance()
        appliance['protocol'] = 'http'
        context = self.context()
        result = self.plugin.create_a10_appliance(context, self.envelope(appliance))
        context.session.commit()
        self.assertIsNot(result['id'], None)
        self.assertEqual(80, result['port'])

    def test_get_a10_appliance(self):
        appliance = self.fake_appliance()
        create_context = self.context()
        create_result = self.plugin.create_a10_appliance(create_context, self.envelope(appliance))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_appliance(context, create_result['id'])

        self.assertEqual(create_result, result)

    def test_get_a10_appliance_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Appliance.A10ApplianceNotFoundError,
            self.plugin.get_a10_appliance,
            context,
            'fake-appliance-id')

    def test_get_a10_appliances(self):
        appliance = self.fake_appliance()
        create_context = self.context()
        create_result = self.plugin.create_a10_appliance(create_context, self.envelope(appliance))
        create_context.session.commit()

        context = self.context()
        result = self.plugin.get_a10_appliances(context)

        self.assertEqual([create_result], result)

    def test_delete_a10_appliance(self):
        appliance = self.fake_appliance()
        create_context = self.context()
        create_result = self.plugin.create_a10_appliance(create_context, self.envelope(appliance))
        create_context.session.commit()

        context = self.context()
        self.plugin.delete_a10_appliance(context, create_result['id'])
        context.session.commit()

        get_context = self.context()
        self.assertRaises(
            a10Appliance.A10ApplianceNotFoundError,
            self.plugin.get_a10_appliance,
            get_context,
            create_result['id'])

    def test_delete_a10_appliance_not_found(self):
        context = self.context()
        self.assertRaises(
            a10Appliance.A10ApplianceNotFoundError,
            self.plugin.delete_a10_appliance,
            context,
            'fake-appliance-id')

    def test_delete_a10_appliance_in_use(self):
        appliance = self.fake_appliance()
        create_context = self.context()
        create_result = self.plugin.create_a10_appliance(create_context, self.envelope(appliance))
        create_context.session.add(
            models.default(
                models.A10SLB,
                a10_appliance_id=create_result['id']
            ))
        create_context.session.commit()

        context = self.context()
        self.assertRaises(
            a10Appliance.A10ApplianceInUseError,
            self.plugin.delete_a10_appliance,
            context,
            create_result['id'])

    def test_update_a10_appliance(self):
        appliance = self.fake_appliance()
        create_context = self.context()
        create_result = self.plugin.create_a10_appliance(create_context, self.envelope(appliance))
        create_context.session.commit()

        change = {
            'api_version': 'other-version'
        }
        expected = create_result.copy()
        expected.update(change)

        context = self.context()
        result = self.plugin.update_a10_appliance(context,
                                                  create_result['id'],
                                                  self.envelope(change))
        context.session.commit()

        self.assertEqual(expected, result)

        get_context = self.context()
        get_result = self.plugin.get_a10_appliance(get_context, create_result['id'])

        self.assertEqual(expected, get_result)

    def test_update_a10_appliance_not_found(self):
        change = {
            'api_version': 'other-version'
        }
        context = self.context()
        self.assertRaises(
            a10Appliance.A10ApplianceNotFoundError,
            self.plugin.update_a10_appliance,
            context,
            'fake-appliance-id', self.envelope(change))

    def test_get_plugin_name(self):
        self.assertIsNot(self.plugin.get_plugin_name(), None)

    def test_get_plugin_description(self):
        self.assertIsNot(self.plugin.get_plugin_description(), None)

    def test_get_plugin_type(self):
        self.assertEqual(self.plugin.get_plugin_type(), constants.A10_APPLIANCE)
