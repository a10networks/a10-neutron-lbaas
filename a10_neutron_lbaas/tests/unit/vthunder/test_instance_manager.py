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
import sys

import a10_neutron_lbaas.tests.unit.mocks as mocks

import a10_neutron_lbaas.a10_exceptions as a10_ex
import a10_neutron_lbaas.tests.unit.test_base as test_base

# Figure out why this is necessary to make the mock work correctly.

log_mock = mock.MagicMock()

# This is here because I couldn't get mock to actually mock the classes
# Get rid of this and I'll give you a cookie - MD
sys.modules["a10_neutronclient"] = mock.MagicMock()
sys.modules["a10_openstack_lib"] = mock.MagicMock()
sys.modules["glanceclient"] = mock.MagicMock()
sys.modules["glanceclient.client"] = mock.MagicMock()
sys.modules["logging"] = mock.Mock(getLogger=mock.Mock(return_value=log_mock))
sys.modules["django"] = mock.MagicMock()
sys.modules["django.conf"] = mock.MagicMock()
sys.modules["django.conf.settings"] = mock.MagicMock()
sys.modules["openstack_dashboard"] = mock.MagicMock()
sys.modules["openstack_dashboard.api"] = mock.MagicMock()
sys.modules["openstack_dashboard.api.neutron"] = mock.MagicMock()
sys.modules["openstack_dashboard.api.neutron.NeutronAPIDictWrapper"] = mock.MagicMock()


# a10 client that extends neutronclient.v2_0.client.Client

import a10_neutron_lbaas.vthunder.instance_manager as im

VMSTATE_KEY = "OS-EXT-STS:vm_state"
DEFAULT_INSTANCE_STATES = [
    "INITALIZED",
    "ACTIVE"
]

instance_states = []


class TestInstanceManager(test_base.UnitTestBase):
    def setUp(self):
        log_mock.reset_mock()
        super(TestInstanceManager, self).setUp()

        im.CREATE_TIMEOUT = 10

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
        self.instance_states = ["ACTIVE",
                                "ACTIVE"]

        self.setup_mocks()
        self.ks_version = 3
        self.auth_url = "http://localhost:1234"
        self.vthunder_tenant_name = "tenantive-tenant"
        self.user = "user"
        self.password = "password"
        self.target = im.InstanceManager(self.ks_version, self.auth_url, self.vthunder_tenant_name,
                                         self.user, self.password, nova_api=self.nova_api,
                                         neutron_api=self.neutron_api)

    def server_get_side_effect(self, args):
        if len(instance_states) > 0:
            vmstate = instance_states.pop()
        else:
            vmstate = "ACTIVE"
        setattr(self.fake_created, VMSTATE_KEY, vmstate)

    def setup_mocks(self):
        self.fake_created = mock.Mock(addresses={"mgmt-net": [
            {
                "version": 4,
                "addr": "127.0.0.1"
            }
        ]})
        setattr(self.fake_created, VMSTATE_KEY, "ACTIVE")

        self.a10_context = mock.MagicMock()
        self.nova_api.servers = mock.Mock()
        self.fake_image = self._fake_image()
        self.fake_flavor = self._fake_flavor()
        self.fake_networks = {
            "networks": [
                {"id": "mgmt-net", "name": "mgmt-net"}]
        }

        self.fake_instance = self._fake_instance(name="fake-instance-01",
                                                 image=self.fake_image.id,
                                                 flavor=self.fake_flavor.id,
                                                 nics=['mgmt-net'])

        self.nova_api.servers.list = mock.Mock(return_value=[self._fake_instance()])
        self.nova_api.servers.create = mock.Mock(return_value=self.fake_created)
        self.nova_api.servers.get = mock.Mock(return_value=self.fake_created)

        self.nova_api.flavors = mock.Mock()
        self.nova_api.flavors.list = mock.Mock(return_value=[self._fake_flavor()])

        self.nova_api.images = mock.Mock()
        self.nova_api.images.list = mock.Mock(return_value=[self._fake_image()])

        self.glance_api.images.list.return_value = [self._fake_image()]

        self.neutron_api.list_networks = mock.Mock(return_value=self.fake_networks)

        self.neutron_api.get_a10_instances = mock.Mock(return_value=[{}])
        self.neutron_api.create_a10_instance = mock.Mock(return_value=self.fake_created)

    def _fake_instance(self, id=1, name="instance001", image=None, flavor=None, nics=[]):
        return mocks.FakeInstance(id=id, name=name, image=image, flavor=flavor, nics=nics)

    def _fake_flavor(self, id=1, name="flavor001"):
        return mocks.FakeFlavor(id=id, name=name)

    def _fake_image(self, id=1, name="image001"):
        import json

        metadata = {
            "properties": json.dumps(
                {
                    "api_version": 2.1,
                    "username": "dude",
                    "password": "password",
                    "protocol": "http",
                    "port": 80
                }
            )
        }
        return mocks.FakeImage(id=id, name=name, metadata=metadata)

    def _test_create(self, instance):
        self.target.create_instance(instance)

    def test_create_calls_nova_api(self):
        self._test_create(self.fake_instance)
        self.assertTrue(self.nova_api.servers.create.called)

    def test_create_calls_nova_api_with_args(self):
        self._test_create(self.fake_instance)
        expected = self.fake_instance.copy()
        expected["nics"] = [{'net-id': x} for x in self.fake_instance["networks"]]
        del expected["networks"]

        self.nova_api.servers.create.assert_called_with(**expected)

    def test_get_instance_gets_image_get(self):
        instance_id = "INSTANCE_ID"
        self.nova_api.servers.get.side_effect = self.server_get_side_effect
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

    def test_neutronapi_notnone(self):
        self.assertIsNotNone(self.target._neutron_api)

    def test_novaapi_notnone(self):
        self.assertIsNotNone(self.target._nova_api)

    def test_create_instance_flavor_not_available_throws_exception(self):
        self.nova_api.flavors.list.return_value = [None]
        fake_instance = self.fake_instance
        with self.assertRaises(a10_ex.FlavorNotFoundError):
            self.target.create_instance(fake_instance)

    def test_create_instance_network_not_available_throws_exception(self):
        self.neutron_api.list_networks.return_value = {"networks": [None]}
        self.neutron_api.list_networks.side_effect = a10_ex.NetworksNotFoundError()
        fake_instance = self.fake_instance
        fake_instance["networks"] = ["fakenet"]

        with self.assertRaises(a10_ex.NetworksNotFoundError):
            self.target.create_instance(fake_instance)

    def test_get_network_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_networks(networks={})

    def test_get_image_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_image(identifier=None)

    def test_get_flavor_throws_exception_for_unspecified_identifier(self):
        with self.assertRaises(a10_ex.IdentifierUnspecifiedError):
            self.target.get_flavor(identifier=None)

    def test_get_flavor_throws_exception_for_missing_flavor(self):
        self.nova_api.flavors.list.return_value = [None]
        self.nova_api.flavors.list.side_effect = a10_ex.FlavorNotFoundError
        with self.assertRaises(a10_ex.FlavorNotFoundError):
            self.target.get_flavor(identifier="invalidflavor")

    def test_get_networks_failure_returns_exception(self):
        self.neutron_api.list_networks.side_effect = a10_ex.ServiceUnavailableError()
        self.neutron_api.list_networks.return_value = {"networks": []}

        with self.assertRaises(a10_ex.NetworksNotFoundError):
            self.target.get_networks(networks=["network"])

    def test_create_device_instance_returns_host(self):
        defaults = im._default_server
        defaults["flavor"] = "flavor001"
        defaults["networks"] = ["mgmt-net"]
        defaults["glance_image"] = "image001"
        defaults["nova_flavor"] = "flavor001"
        defaults["vthunder_management_network"] = "mgmt-net"
        defaults["vthunder_data_networks"] = ["mgmt-net"]

        self.fake_created.addresses = dict((network, [
            {
                "version": 4,
                "addr": "127.0.0.1"
            }
        ]) for network in defaults['networks'])

        self.nova_api.flavors.list.return_value = [self._fake_flavor(
            name=defaults['flavor'])]

        self.neutron_api.list_networks.return_value = {
            "networks": [{"id": x, "name": x}
                         for x in defaults['networks']]
        }

        device = self.target.create_device_instance(defaults)
        self.assertEqual('127.0.0.1', device['ip_address'])
