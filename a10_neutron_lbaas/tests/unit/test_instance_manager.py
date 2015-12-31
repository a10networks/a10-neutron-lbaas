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
import test_base

import mocks
import sys

import a10_neutron_lbaas.a10_exceptions as a10_ex

# Figure out why this is necessary to make the mock work correctly.

log_mock = mock.MagicMock()

sys.modules["glanceclient"] = mock.MagicMock()
sys.modules["glanceclient.client"] = mock.MagicMock()
sys.modules["logging"] = mock.Mock(getLogger=mock.Mock(return_value=log_mock))

import a10_neutron_lbaas.instance_manager as im


class TestInstanceManager(test_base.UnitTestBase):
    def setUp(self):
        log_mock.reset_mock()
        super(TestInstanceManager, self).setUp()
        glance_patch = mock.patch("glanceclient.client")
        self.glance_api = glance_patch.start()
        self.addCleanup(glance_patch.stop)

        keystone_patch = mock.patch("keystoneclient.client.Client")
        self.keystone_api = keystone_patch.start()
        self.addCleanup(keystone_patch.stop)

        neutron_patch = mock.patch("neutronclient.neutron.client.Client")
        self.neutron_api = neutron_patch.start()
        self.addCleanup(neutron_patch.stop)

        nova_patch = mock.patch("novaclient.client.Client")
        self.nova_api = nova_patch.start()
        self.addCleanup(nova_patch.stop)
        self.setup_mocks()

        self.target = im.InstanceManager(context=self.os_context, request=self.request,
                                         nova_api=self.nova_api,
                                         glance_api=self.glance_api, neutron_api=self.neutron_api,
                                         keystone_api=self.keystone_api)

    def setup_mocks(self):
        self.a10_context = mock.MagicMock()
        self.os_context = mock.MagicMock()
        self.nova_api.servers = mock.Mock()
        self.fake_image = self._fake_image()
        self.fake_flavor = self._fake_flavor()
        self.fake_networks = {"networks": [{"net-id": "net01"}, {"net-id": "net02"}]}

        self.fake_instance = self._fake_instance(name="fake-instance-01",
                                                 image=self.fake_image.id,
                                                 flavor=self.fake_flavor.id,
                                                 nics=self.fake_networks.get("networks"))

        self.service_catalog = [{
            "name": "keystone",
            "type": "identity",
            "endpoints": [{
                "interface": "public",
                "url": "http://localhost:5000"}]
        }]

        project = {"id": "fakeid", "name": "Carl Adultman"}
        self.token = mock.NonCallableMock(serviceCatalog=self.service_catalog, project=project)
        self.user = mock.NonCallableMock(token=self.token)
        self.request = mock.NonCallableMock(user=self.user)

        self.nova_api.servers.list = mock.Mock(return_value=[self._fake_instance()])
        self.nova_api.flavors = mock.Mock()

        self.nova_api.flavors.list = mock.Mock(return_value=[self._fake_flavor()])
        self.nova_api.images = mock.Mock()

        self.nova_api.images.list = mock.Mock(return_value=[self._fake_image()])
        self.neutron_api.list_networks = mock.Mock(return_value=self.fake_networks)

    def _fake_instance(self, id=1, name="instance001", image=None, flavor=None, nics=[]):
        return mocks.FakeInstance(id=id, name=name, image=image, flavor=flavor, nics=nics)

    def _fake_flavor(self, id=1, name="flavor001"):
        return mocks.FakeFlavor(id=id, name=name)

    def _fake_image(self, id=1, name="image001"):
        return mocks.FakeImage(id=id, name=name)

    def _test_create(self, instance):
        self.target.create_instance(self.os_context, instance)

    def test_create_calls_nova_api(self):
        self._test_create(self.fake_instance)
        self.assertTrue(self.nova_api.servers.create.called)

    def test_create_calls_nova_api_with_args(self):
        fake_instance = self.fake_instance
        self._test_create(fake_instance)
        self.nova_api.servers.create.assert_called_with(**fake_instance)

    def test_get_instance_gets_image_get(self):
        instance_id = "INSTANCE_ID"
        self.target.get_instance(instance_id)
        self.nova_api.flavors.list.assert_called()

    def test_delete_instance_calls_nova(self):
        fake_instance = self._fake_instance()
        self.target.delete_instance(fake_instance["id"])
        self.nova_api.servers.delete.assert_called_with(fake_instance["id"])

    def test_list_instances_calls_nova_list(self):
        detailed = True
        search_opts = None
        marker = None
        limit = None
        sort_keys = None
        sort_dirs = None

        self.target.list_instances(detailed, search_opts, marker, limit, sort_keys, sort_dirs)
        self.nova_api.servers.list.assert_called_with(detailed, search_opts, marker, limit,
                                                      sort_keys, sort_dirs)

    def test_token_contains_service_catalog(self):
        self.assertIsNotNone(self.target.endpoints)
        self.assertGreater(len(self.target.endpoints), 0)

    def test_missing_service_catalog_raises_exception(self):
        self.token.serviceCatalog = []
        with self.assertRaises(AttributeError):
            self.target = im.InstanceManager(context=self.os_context,
                                             request=self.request,
                                             nova_api=self.nova_api,
                                             glance_api=self.glance_api,
                                             neutron_api=self.neutron_api,
                                             keystone_api=self.keystone_api)

    def test_keystoneapi_notnone(self):
        self.assertIsNotNone(self.target._keystone_api)

    def test_glanceapi_notnone(self):
        self.assertIsNotNone(self.target._glance_api)

    def test_neutronapi_notnone(self):
        self.assertIsNotNone(self.target._neutron_api)

    def test_novaapi_notnone(self):
        self.assertIsNotNone(self.target._nova_api)

    def test_create_instance_image_not_available_throws_exception(self):
        self.nova_api.images.list.return_value = None
        self.nova_api.images.list.side_effect = a10_ex.ImageNotFoundError()
        fake_instance = self.fake_instance
        with self.assertRaises(a10_ex.ImageNotFoundError):
            self.target.create_instance(self.os_context, fake_instance)

    def test_create_instance_flavor_not_available_throws_exception(self):
        self.nova_api.flavors.list.return_value = [None]
        fake_instance = self.fake_instance
        with self.assertRaises(a10_ex.FlavorNotFoundError):
            self.target.create_instance(self.os_context, fake_instance)

    def test_create_instance_network_not_available_throws_exception(self):
        self.neutron_api.list_networks.return_value = {"networks": [None]}
        self.neutron_api.list_networks.side_effect = a10_ex.NetworksNotFoundError()
        fake_instance = self.fake_instance
        fake_instance["networks"] = ["fakenet"]

        with self.assertRaises(a10_ex.NetworksNotFoundError):
            self.target.create_instance(self.os_context, fake_instance)

    def test_get_network_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_networks(self.os_context, networks={})

    def test_get_image_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_image(self.os_context, identifier=None)

    def test_get_image_throws_exception_for_missing_image(self):
        self.nova_api.images.list.return_value = [None]
        with self.assertRaises(a10_ex.ImageNotFoundError):
            self.nova_api.images.list.return_value = None
            self.nova_api.images.list.side_effect = a10_ex.ImageNotFoundError()
            self.target.get_image(self.os_context, identifier="invalidimage")

    def test_get_flavor_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_flavor(self.os_context, identifier=None)

    def test_get_flavor_throws_exception_for_missing_flavor(self):
        self.nova_api.flavors.list.return_value = [None]
        self.nova_api.flavors.list.side_effect = a10_ex.FlavorNotFoundError
        with self.assertRaises(a10_ex.FlavorNotFoundError):
            self.target.get_flavor(self.os_context, identifier="invalidflavor")

    def test_token_missing_endpoints_logs_exception(self):
        self.token.serviceCatalog = []
        self.target._get_auth_from_token(self.token)
        log_mock.exception.assert_called()

    def test_get_networks_failure_returns_exception(self):
        self.neutron_api.list_networks.side_effect = a10_ex.ServiceUnavailableError()
        self.neutron_api.list_networks.return_value = {"networks": []}

        with self.assertRaises(a10_ex.NetworksNotFoundError):
            self.target.get_networks(self.os_context, networks=[{"network"}])
