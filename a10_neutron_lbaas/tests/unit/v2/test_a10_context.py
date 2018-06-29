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
import sys
import types

import fake_objs
import mocks
import test_base
import a10_neutron_lbaas.v2.v2_context as a10


class FakeException(Exception):
    pass


class TestA10Context(test_base.UnitTestBase):

    def _build_openstack_context(self):
        admin_context = {
            "tenant_id": "admin"
        }

        return mock.Mock(get_admin_context=mock.Mock(return_value=admin_context))

    def _py2_copy(self, func):
        copy_func = types.FunctionType(func.func_code, func.func_globals,
                                       name=func.func_name,
                                       argdefs=func.func_defaults,
                                       closure=func.func_closure)
        return copy_func

    def _py3_copy(self, func):
        copy_func = types.FunctionType(func.__code__,
                                       func.__globals__,
                                       name=func.__name__,
                                       argdefs=func.__defaults__,
                                       closure=func.__closure__)
        return copy_func

    def _copy_func(self, func):
        if sys.version_info[0] == 2:
            return self._py2_copy(func)
        else:
            return self._py3_copy(func)

    def _clean_import(self):
        a10.a10_context.A10Context.get_partition_key = self.partition_key_save

    def setUp(self, **kwargs):
        super(TestA10Context, self).setUp(**kwargs)
        self.handler = self.a.pool
        self.ctx = self._build_openstack_context()
        self.m = fake_objs.FakeLoadBalancer()
        self.partition_key_save = self._copy_func(a10.a10_context.A10Context.get_partition_key)
        self.addCleanup(self._clean_import)
        a10.a10_context.A10Context.get_partition_key = mock.Mock()
        a10.a10_context.A10Context.partition_key = 'get-off-my-lawn'

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

    def test_write(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='ax-write') as c:
            c
        self.a.last_client.system.action.write_memory.assert_called()
        self.a.last_client.session.close.assert_called_with()

    def test_write_no_write(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='ax-nowrite') as c:
            c
        self.a.last_client.system.action.write_memory.assert_not_called()
        self.a.last_client.session.close.assert_called_with()

    def test_write_e(self):
        try:
            with a10.A10WriteContext(self.handler, self.ctx, self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.empty_close_mocks()

    def test_write_status(self):
        with a10.A10WriteStatusContext(self.handler, self.ctx, self.m) as c:
            c
        self.print_mocks()
        self.a.openstack_driver.pool.successful_completion.assert_called_with(
            self.ctx, self.m)

    def test_write_status_e(self):
        try:
            with a10.A10WriteStatusContext(self.handler, self.ctx,
                                           self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.a.openstack_driver.pool.failed_completion.assert_called_with(
                self.ctx, self.m)

    def test_delete(self):
        with a10.A10DeleteContext(self.handler, self.ctx, self.m) as c:
            c
        self.print_mocks()
        self.a.openstack_driver.pool.successful_completion.assert_called_with(
            self.ctx, self.m, delete=True)

    def test_delete_e(self):
        try:
            with a10.A10DeleteContext(self.handler, self.ctx, self.m) as c:
                c
                raise FakeException()
        except FakeException:
            self.empty_close_mocks()

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
            self.m.tenant_id[0:13])

    def empty_close_mocks(self):
        self.print_mocks()
        self.assertEqual(0, len(self.a.openstack_driver.mock_calls))
        self.assertEqual(2, len(self.a.last_client.mock_calls))
        self.a.last_client.session.close.assert_called_with()

    def test_partition_name(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_name, self.m.tenant_id[0:13])

    def test_partition_name_withalt(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-alt') as c:
            # shared_partition has no effect on an ADP configured device
            self.assertEqual(c.partition_name, self.m.tenant_id[0:13])


class TestA10ContextHA(TestA10Context):

    def test_ha(self):
        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='ax4') as c:
            c
        self.a.last_client.ha.sync.assert_called_with('1.1.1.1', 'admin', 'a10')
        self.a.last_client.session.close.assert_called_with()
