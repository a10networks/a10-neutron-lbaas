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
import test_base


def return_one(*args):
    return 1


def return_two(*args):
    return 2


class TestMembers(test_base.UnitTestBase):

    def set_count_1(self):
        self.a.member.openstack_manager._count = return_one

    def set_count_2(self):
        self.a.member.openstack_manager._count = return_two

    def test_get_ip(self):
        m = test_base.FakeMember(pool=mock.MagicMock())
        self.a.member._get_ip(None, m, False)
        self.a.openstack_driver.member._get_ip.assert_called_with(
            None, m, False)

    def test_get_name(self):
        m = test_base.FakeMember(pool=mock.MagicMock())
        z = self.a.member._get_name(m, '1.1.1.1')
        self.assertEqual(z, '_get-o_1_1_1_1_neutron')

    def test_count(self):
        self.a.member._count(None, test_base.FakeMember(pool=mock.MagicMock()))

    def test_create(self, admin_state_up=True):
        m = test_base.FakeMember(admin_state_up=admin_state_up,
                                 pool=mock.MagicMock())
        ip = self.a.member._get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)
        self.a.member.create(None, m)

        self.a.last_client.slb.server.create.assert_called_with(name, ip)
        if admin_state_up:
            status = self.a.last_client.slb.UP
        else:
            status = self.a.last_client.slb.DOWN
        self.a.last_client.slb.service_group.member.create.assert_called_with(
            m.pool.id, name, m.protocol_port, status=status)

    def test_create_down(self):
        self.test_create(False)

    def test_update_down(self):
        m = test_base.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member._get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)
        self.a.member.update(None, m, m)

        self.a.last_client.slb.service_group.member.update.assert_called_with(
            m.pool.id, name, m.protocol_port, self.a.last_client.slb.DOWN)

    def test_delete(self):
        m = test_base.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member._get_ip(None, m, True)

        self.set_count_1()
        self.a.member.delete(None, m)

        self.a.last_client.slb.server.delete(ip)

    def test_delete_count_gt_one(self):
        m = test_base.FakeMember(False, pool=mock.MagicMock())
        ip = self.a.member._get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)

        self.set_count_2()
        self.a.member.delete(None, m)

        self.a.last_client.slb.service_group.member.delete.assert_called_with(
            m.pool.id, name, m.protocol_port)
