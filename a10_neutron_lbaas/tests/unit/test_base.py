# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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

import os

import a10_neutron_lbaas.tests.test_case as test_case
import mock

import a10_neutron_lbaas.a10_openstack_lb as a10_os
import a10_neutron_lbaas.plumbing_hooks as hooks


def _build_openstack_context():
    admin_context = {
        "tenant_id": "admin"
    }

    return mock.Mock(admin_context=admin_context)


def _build_class_instance_mock():
    instance_mock = mock.MagicMock()
    class_mock = mock.MagicMock()
    class_mock.return_value = instance_mock

    return (class_mock, instance_mock)


class FakeA10OpenstackLB(object):

    def __init__(self, openstack_driver, **kw):
        super(FakeA10OpenstackLB, self).__init__(
            mock.MagicMock(),
            **kw)
        self.openstack_context = _build_openstack_context()

    def _get_a10_client(self, device_info):
        self.device_info = device_info
        self.last_client = mock.MagicMock()
        self.plumbing_hooks = hooks.PlumbingHooks(self)
        return self.last_client

    def reset_mocks(self):
        self.openstack_driver = mock.MagicMock()
        self.last_client = self._get_a10_client(self.device_info)
        return self.last_client


class FakeA10OpenstackLBV1(FakeA10OpenstackLB, a10_os.A10OpenstackLBV1):
    pass


class FakeA10OpenstackLBV2(FakeA10OpenstackLB, a10_os.A10OpenstackLBV2):

    def __init__(self, openstack_driver, **kw):
        super(FakeA10OpenstackLBV2, self).__init__(
            openstack_driver,
            neutron_hooks_module=mock.MagicMock(),
            **kw)
        self.certmgr = mock.Mock()


class UnitTestBase(test_case.TestCase):

    def _build_openstack_context(self):
        return _build_openstack_context()

    def setUp(self):
        unit_dir = os.path.dirname(__file__)
        unit_config = os.path.join(unit_dir, "unit_config")
        os.environ['A10_CONFIG_DIR'] = unit_config

        if not hasattr(self, 'version') or self.version == 'v2':
            self.a = FakeA10OpenstackLBV2(None)
        else:
            self.a = FakeA10OpenstackLBV1(None)

    def print_mocks(self):
        print("OPENSTACK ", self.a.openstack_driver.mock_calls)
        print("CLIENT ", self.a.last_client.mock_calls)

    def empty_mocks(self):
        self.print_mocks()
        self.assertEqual(0, len(self.a.openstack_driver.mock_calls))
        self.assertEqual(0, len(self.a.last_client.mock_calls))

    def empty_close_mocks(self):
        self.print_mocks()
        self.assertEqual(0, len(self.a.openstack_driver.mock_calls))
        self.assertEqual(1, len(self.a.last_client.mock_calls))
        self.a.last_client.session.close.assert_called_with()
