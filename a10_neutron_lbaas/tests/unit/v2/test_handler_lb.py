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

import a10_neutron_lbaas.a10_exceptions as a10_ex
import fake_objs
import test_base


class TestLB(test_base.HandlerTestBase):

    def test_create(self):
        m = fake_objs.FakeLoadBalancer()
        self.a.lb.create(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.create' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('5.5.5.5' in s)
        self.assertTrue('UP' in s)

    def test_create_default_vrid_none_v21(self):
        self._test_create_default_vrid("2.1", None)

    def test_create_default_vrid_set_v21(self):
        self._test_create_default_vrid("2.1", 7)

    def test_create_default_vrid_none_v30(self):
        self._test_create_default_vrid("3.0", None)

    def test_create_default_vrid_set_v30(self):
        self._test_create_default_vrid("3.0", 7)

    def _test_create_default_vrid(self, api_ver=None, default_vrid=None):

        """
        Due to how the config is pulled in, we override the config
        for all of the devices.
        """

        for k, v in self.a.config.get_devices().items():
            v['api_version'] = api_ver
            v['default_virtual_server_vrid'] = default_vrid

        lb = fake_objs.FakeLoadBalancer()
        self.a.lb.create(None, lb)

        create = self.a.last_client.slb.virtual_server.create
        create.assert_has_calls([mock.ANY])
        calls = create.call_args_list

        if default_vrid is not None:
            self.assertIn('vrid=%s' % default_vrid, str(calls))
        if default_vrid is None:
            foundVrid = any(
                'vrid' in x.get('axapi_args', {}).get('virtual_server', {})
                for (_, x) in calls)
            self.assertFalse(
                foundVrid,
                'Expected to find no vrid in {0}'.format(str(calls)))

    # There's no code that causes listeners to be added
    # if they are present when the pool is created.
    # We'd use unittest.skip if it worked with cursed 2.6

    # def test_create_with_listeners(self):
    #     pool = test_base.FakePool('HTTP', 'ROUND_ROBIN', None)
    #     m = test_base.FakeLoadBalancer()
    #     for x in [1, 2, 3]:
    #         z = test_base.FakeListener('TCP', 2222+x, pool=pool,
    #                                    loadbalancer=m)
    #         m.listeners.append(z)
    #     self.a.lb.create(None, m)
    #     s = str(self.a.last_client.mock_calls)
    #     print ("LAST CALLS {0}".format(s))
    #     self.assertTrue('call.slb.virtual_server.create' in s)
    #     self.assertTrue('fake-lb-id-001' in s)
    #     self.assertTrue('5.5.5.5' in s)
    #     self.assertTrue('UP' in s)
    #     self.assertTrue('vport.create' in s)
    #     for x in [1, 2, 3]:
    #         self.assertTrue(str(2222+x) in s)

    def test_update_down(self):
        m = fake_objs.FakeLoadBalancer()
        m.admin_state_up = False
        self.a.lb.update(None, m, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.update' in s)
        self.assertTrue('fake-lb-id-001' in s)
        self.assertTrue('5.5.5.5' in s)
        self.assertTrue('DOWN' in s)

    def test_delete(self):
        m = fake_objs.FakeLoadBalancer()
        self.a.lb.delete(None, m)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.delete' in s)
        self.assertTrue(m.id in s)

    def test_delete_removes_slb(self):
        m = fake_objs.FakeLoadBalancer()
        self.a.lb.delete(None, m)

    def test_refresh(self):
        try:
            self.a.lb.refresh(None, fake_objs.FakeLoadBalancer())
        except a10_ex.UnsupportedFeature:
            pass

    def test_stats_v30(self):
        test_lb = fake_objs.FakeLoadBalancer()
        test_lb.stats_v30()
        c = mock.MagicMock()
        c.client.slb.virtual_server.get = mock.Mock(return_value=test_lb.virt_server)
        c.client.slb.service_group.stats = mock.Mock(return_value=test_lb.service_group)
        c.client.slb.service_group.get = mock.Mock(return_value=test_lb.members)
        ret_val = self.a.lb._stats_v30(c, test_lb.port_list, None)

        self.print_mocks()
        self.assertEqual(ret_val, test_lb.ret_stats_v30)

    def test_stats_v21(self):
        test_lb = fake_objs.FakeLoadBalancer()
        test_lb.stats_v21()
        c = mock.MagicMock()
        c.client.slb.virtual_service.get = mock.Mock(return_value=test_lb.virt_service)
        c.client.slb.service_group.stats = mock.Mock(return_value=test_lb.serv_group)
        ret_val = self.a.lb._stats_v21(c, test_lb.virt_server)

        self.print_mocks()
        self.assertEqual(ret_val, test_lb.ret_stats)

    def test_stats(self):
        test_lb = fake_objs.FakeLoadBalancer()
        self.a.lb.stats(None, test_lb)

        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('call.slb.virtual_server.stats' in s)

    def do_raise_exception(self, e, msg="mock raised exception"):
        def raise_exception(e, msg="acos broke!"):
            raise e(msg)

        return lambda *args, **kwargs: raise_exception(e, msg)

    def _test_create_expressions(self, os_name, pattern, expressions=None):
        self.a.config.get_virtual_server_expressions = self._get_expressions_mock
        expressions = expressions or self.a.config.get_virtual_server_expressions()
        expected = expressions.get(pattern, {}).get("json", None) or ""

        m = fake_objs.FakeLoadBalancer()
        m.name = os_name
        handler = self.a.lb
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("virtual_server.create", s)
        self.assertIn(str(expected), s)

    def test_create_expressions_none(self):
        self._test_create_expressions("mylb", None, {})

    def test_create_expressions_match_beginning(self):
        self._test_create_expressions("securelb", self.EXPR_BEGIN)

    def test_create_expressions_match_end(self):
        self._test_create_expressions("lbweb", self.EXPR_END)

    def test_create_expressions_match_charclass(self):
        self._test_create_expressions("lbwwlb", self.EXPR_CLASS)

    def test_create_expressions_nomatch(self):
        self.a.config.get_virtual_server_expressions = self._get_expressions_mock
        expressions = self.a.config.get_virtual_server_expressions()
        expected = expressions.get(self.EXPR_BEGIN, {}).get("json", None) or ""

        m = fake_objs.FakeLoadBalancer()
        m.name = "mylb"
        handler = self.a.lb
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("virtual_server.create", s)
        self.assertNotIn(str(expected), s)

    def test_create_noname_noexception(self):
        self.a.config.get_virtual_server_expressions = self._get_expressions_mock
        expressions = self.a.config.get_virtual_server_expressions()

        expected = expressions.get(self.EXPR_BEGIN, {}).get("json", None) or ""

        m = fake_objs.FakeLoadBalancer()
        m.name = None
        handler = self.a.lb
        handler.create(None, m)

        s = str(self.a.last_client.mock_calls)
        self.assertIn("virtual_server.create", s)
        self.assertNotIn(str(expected), s)
