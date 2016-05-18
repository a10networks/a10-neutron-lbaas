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

import mock

import a10_neutron_lbaas.v1.v1_context as a10

import test_base


class FakeException(Exception):
    pass


class TestA10Context(test_base.UnitTestBase):

    def setUp(self, **kwargs):
        super(TestA10Context, self).setUp(**kwargs)
        self.handler = self.a.pool
        self.ctx = self._build_openstack_context()
        self.m = {'id': 'fake-id-001', 'tenant_id': 'faketen1'}

    def test_context(self):
        with a10.A10Context(self.handler, self.ctx, self.m) as c:
            self.empty_mocks()
            c
        self.empty_close_mocks()

    def test_context_e(self):
        try:
            with a10.A10Context(self.handler, self.ctx, self.m) as c:
                self.empty_mocks()
                c
                raise FakeException()
        except FakeException:
            self.empty_close_mocks()

    def _set_api_version(self, api_version="2.1"):
        for k, v in self.a.config.get("devices").items():
            v['api_version'] = api_version

    def test_write_v21(self):
        self._set_api_version()
        with a10.A10WriteContext(self.handler, self.ctx, self.m) as c:
            c
        self.a.last_client.system.action.activate_and_write.assert_called(None, "shared")
        self.a.last_client.session.close.assert_called_with()

    def test_write_v30(self):
        self._set_api_version("3.0")
        with a10.A10WriteContext(self.handler, self.ctx, self.m) as c:
            c
        self.a.last_client.system.action.write_memory.assert_called()
        self.a.last_client.session.close.assert_called_with()

    def test_write_e(self):
        try:
            with a10.A10WriteContext(self.handler, self.ctx, self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.empty_close_mocks()
            pass

    def test_write_status(self):
        with a10.A10WriteStatusContext(self.handler, self.ctx, self.m) as c:
            c
        self.a.openstack_driver._active.assert_called_with(
            self.ctx, 'pool', 'fake-id-001')

    def test_write_status_e(self):
        try:
            with a10.A10WriteStatusContext(self.handler, self.ctx,
                                           self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.a.openstack_driver._failed.assert_called_with(
                self.ctx, 'pool', 'fake-id-001')
            pass

    def test_delete(self):
        with a10.A10DeleteContext(self.handler, self.ctx, self.m) as c:
            c
        self.a.openstack_driver._db_delete.assert_called_with(
            self.ctx, 'pool', 'fake-id-001')

    def test_delete_e(self):
        try:
            with a10.A10DeleteContext(self.handler, self.ctx, self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.empty_close_mocks()
            pass

    def test_partition_name(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_name, 'shared')

    def test_partition_name_withalt(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-alt') as c:
            self.assertEqual(c.partition_name, 'mypart')


# Re-run all the context manager tests with appliance partitioning.
class TestA10ContextADP(TestA10Context):

    def setUp(self):
        super(TestA10ContextADP, self).setUp()
        self.reset_v_method('adp')

    def tearDown(self):
        self.reset_v_method('lsi')

    def reset_v_method(self, val):
        for k, v in self.a.config.get_devices().items():
            v['v_method'] = val

    def empty_mocks(self):
        self.print_mocks()
        self.assertEqual(0, len(self.a.openstack_driver.mock_calls))
        self.assertEqual(1, len(self.a.last_client.mock_calls))
        self.a.last_client.system.partition.active.assert_called_with(
            self.m['tenant_id'])

    def empty_close_mocks(self):
        self.print_mocks()
        self.assertEqual(0, len(self.a.openstack_driver.mock_calls))
        self.assertEqual(2, len(self.a.last_client.mock_calls))
        self.a.last_client.session.close.assert_called_with()

    def test_write_v21(self):
        self._set_api_version("2.1")
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            c
        self.a.last_client.system.action.activate_and_write.assert_called_with(
            mock.ANY)
        self.a.last_client.session.close.assert_called_with()

    def test_write_v30(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            c
        self.a.last_client.system.action.activate_and_write.assert_called_with(mock.ANY)
        self.a.last_client.session.close.assert_called_with()

    def test_write_v21_deleted_partition(self):
        self._set_api_version("2.1")
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            c
            c.partition_name = None

        self.a.last_client.system.action.activate_and_write.assert_called_with(None)
        self.a.last_client.session.close.assert_called_with()

    def test_write_v21_partition(self):
        self._set_api_version("2.1")
        expected = "part1"
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            c
            c.partition_name = expected

        self.a.last_client.system.action.activate_and_write.assert_called_with(expected)
        self.a.last_client.session.close.assert_called_with()

    def test_partition_name(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_name, self.m['tenant_id'][0:13])

    def test_partition_name_withalt(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-alt') as c:
            # shared_partition has no effect on an ADP configured device
            self.assertEqual(c.partition_name, self.m['tenant_id'][0:13])


class TestA10ContextHA(TestA10Context):

    def setUp(self):
        super(TestA10ContextHA, self).setUp()

    def test_ha(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='ax4') as c:
            c
        self.a.last_client.ha.sync.assert_called_with('1.1.1.1', 'admin', 'a10')
