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

import logging
import mock

import a10_neutron_lbaas.a10_exceptions as a10_ex
import fake_objs
import test_base

LOG = logging.getLogger(__name__)


def return_one(*args):
    return 1


def return_two(*args):
    return 2


class TestMembers(test_base.HandlerTestBase):

    def set_count_1(self):
        self.a.member.neutron.member_count = return_one

    def set_count_2(self):
        self.a.member.neutron.member_count = return_two

    def test_get_ip(self):
        m = fake_objs.FakeMember(pool=mock.MagicMock())
        self.a.member.neutron.member_get_ip(None, m, False)
        self.print_mocks()
        self.a.neutron.member_get_ip.assert_called_with(
            None, m, False)

    def test_get_name(self):
        m = fake_objs.FakeMember(pool=mock.MagicMock())
        z = self.a.member._get_name(m, '1.1.1.1')
        self.assertEqual(z, '_get-o_1_1_1_1_neutron')

    def test_count(self):
        self.a.member.neutron.member_count(
            None, fake_objs.FakeMember(pool=mock.MagicMock()))

    def _test_create(self, admin_state_up=True, uuid_name=False, conn_limit=8000000):
        if uuid_name:
            old = self.a.config.get('member_name_use_uuid')
            self.a.config._config.member_name_use_uuid = True

        m = fake_objs.FakeMember(admin_state_up=admin_state_up,
                                 pool=mock.MagicMock())
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        if uuid_name:
            name = m.id
        else:
            name = self.a.member._get_name(m, ip)
        self.a.member.create(None, m)

        if admin_state_up:
            status = self.a.last_client.slb.UP
        else:
            status = self.a.last_client.slb.DOWN
        # TODO(mdurrant) - can we do this a better way without an if?
        if conn_limit < 1 or conn_limit > 8000000:
            self.a.last_client.slb.server.create.assert_called_with(
                name, ip,
                status=status,
                config_defaults=mock.ANY,
                axapi_args={'server': {}})
        else:
            self.a.last_client.slb.server.create.assert_called_with(
                name, ip,
                status=status,
                config_defaults=mock.ANY,
                axapi_args={'server': {'conn-limit': conn_limit}})
        self.a.last_client.slb.service_group.member.create.assert_called_with(
            m.pool.id, name, m.protocol_port, status=status,
            axapi_args={'member': {}})
        if uuid_name:
            self.a.config._config.member_name_use_uuid = old

    def test_create_connlimit(self):
        for k, v in self.a.config.get_devices().items():
            v['conn-limit'] = 1337
        self._test_create(conn_limit=1337)

    def test_create_connlimit_oob(self):
        for k, v in self.a.config.get_devices().items():
            v['conn-limit'] = 8000001
        try:
            self._test_create(conn_limit=8000001)
        except a10_ex.ConnLimitOutOfBounds:
            pass

    def test_create_connlimit_uob(self):
        for k, v in self.a.config.get_devices().items():
            v['conn-limit'] = 0
        try:
            self._test_create(conn_limit=0)
        except a10_ex.ConnLimitOutOfBounds:
            pass

    def test_update_down(self):
        m = fake_objs.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)
        self.a.member.update(None, m, m)

        self.a.last_client.slb.service_group.member.update.assert_called_with(
            m.pool.id, name, m.protocol_port, self.a.last_client.slb.DOWN,
            axapi_args={'member': {}})

    def test_delete(self):
        m = fake_objs.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member.neutron.member_get_ip(None, m, True)

        self.set_count_1()
        self.a.member.delete(None, m)

        self.a.last_client.slb.server.delete(ip)

    def test_delete_count_gt_one(self):
        m = fake_objs.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)

        self.set_count_2()
        self.a.member.delete(None, m)

        self.a.last_client.slb.service_group.member.delete.assert_called_with(
            m.pool_id, name, m.protocol_port)

    def _test_create_expressions(self, os_name, pattern, expressions=None):
        self.a.config.get_member_expressions = self._get_expressions_mock
        expressions = expressions or self.a.config.get_member_expressions()
        expected = expressions.get(pattern, {}).get("json", {})
        admin_state = self.a.last_client.slb.UP
        m = fake_objs.FakeMember(admin_state_up=admin_state,
                                 pool=mock.MagicMock())

        m.name = os_name

        handler = self.a.member
        handler.create(None, m)

        # s = str(self.a.last_client.mock_calls)
        self.a.last_client.slb.server.create.assert_called_with(
            mock.ANY,
            mock.ANY,
            status=mock.ANY,
            config_defaults=expected,
            axapi_args={'server': {}})
        # self.assertIn("member.create", s)
        # self.assertIn(str(expected), s)

    def test_create_expressions_none(self):
        self._test_create_expressions("server", None, {})

    def test_create_expressions_match_beginning(self):
        self._test_create_expressions("secureserver", self.EXPR_BEGIN)

    def test_create_expressions_match_end(self):
        self._test_create_expressions("serverweb", self.EXPR_END)

    def test_create_expressions_match_charclass(self):
        self._test_create_expressions("serverwwserver", self.EXPR_CLASS)

    def test_create_expressions_nomatch(self):
        self.a.config.get_member_expressions = self._get_expressions_mock

        admin_state = self.a.last_client.slb.UP
        m = fake_objs.FakeMember(admin_state_up=admin_state,
                                 pool=mock.MagicMock())

        m.name = "myserver"

        handler = self.a.member
        handler.create(None, m)

        self.a.last_client.slb.server.create.assert_called_with(
            mock.ANY, mock.ANY,
            status=mock.ANY,
            config_defaults={},
            axapi_args={'server': {}})

    def test_create_empty_name_noexception(self):
        self.a.config.get_member_expressions = self._get_expressions_mock

        admin_state = self.a.last_client.slb.UP
        m = fake_objs.FakeMember(admin_state_up=admin_state,
                                 pool=mock.MagicMock())

        m.name = None

        handler = self.a.member
        handler.create(None, m)

        self.a.last_client.slb.server.create.assert_called_with(
            mock.ANY, mock.ANY,
            status=mock.ANY,
            config_defaults={},
            axapi_args={'server': {}})
