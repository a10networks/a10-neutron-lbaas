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

import fake_objs
import test_base


def return_one(*args):
    return 1


def return_two(*args):
    return 2


class TestMembers(test_base.UnitTestBase):

    def set_count_1(self):
        self.a.openstack_driver._member_count = return_one

    def set_count_2(self):
        self.a.openstack_driver._member_count = return_two

    def test_get_ip(self):
        m = fake_objs.FakeMember()
        self.a.member.neutron.member_get_ip(None, m, False)
        self.a.openstack_driver._member_get_ip.assert_called_with(
            None, m, False)

    def test_get_name(self):
        m = fake_objs.FakeMember()
        z = self.a.member._get_name(m, '1.1.1.1')
        self.assertEqual(z, '_ten1_1_1_1_1_neutron')

    def test_count(self):
        self.a.member.neutron.member_count(None, fake_objs.FakeMember())

    def _test_create(self, admin_state_up=True, uuid_name=False):
        if uuid_name:
            old = self.a.config.get('member_name_use_uuid')
            self.a.config._config.member_name_use_uuid = True
        m = fake_objs.FakeMember(admin_state_up=admin_state_up)
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        if uuid_name:
            name = m['id']
        else:
            name = self.a.member._get_name(m, ip)
        self.a.member.create(None, m)

        if admin_state_up:
            status = self.a.last_client.slb.UP
        else:
            status = self.a.last_client.slb.DOWN
        self.a.last_client.slb.server.create.assert_called_with(
            name, ip,
            status=status,
            axapi_args={'server': {}})
        pool_name = self.a.member._pool_name(None, m['pool_id'])
        self.a.last_client.slb.service_group.member.create.assert_called_with(
            pool_name, name, m['protocol_port'], status=status,
            axapi_args={'member': {}})
        if uuid_name:
            self.a.config._config.member_name_use_uuid = old

    def test_create(self, admin_state_up=True):
        self._test_create()

    def test_create_member_uuid(self):
        self._test_create(uuid_name=True)

    def test_create_down(self):
        self._test_create(admin_state_up=False)

    def test_update_down(self):
        m = fake_objs.FakeMember(admin_state_up=False)
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)
        self.a.member.update(None, m, m)

        pool_name = self.a.member._pool_name(None, m['pool_id'])
        self.a.last_client.slb.service_group.member.update.assert_called_with(
            pool_name, name, m['protocol_port'],
            self.a.last_client.slb.DOWN,
            axapi_args={'member': {}})

    def test_delete(self):
        m = fake_objs.FakeMember()
        ip = self.a.member.neutron.member_get_ip(None, m, True)

        self.set_count_1()
        self.a.member.delete(None, m)

        self.a.last_client.slb.server.delete(ip)

    def test_delete_count_gt_one(self):
        m = fake_objs.FakeMember()
        ip = self.a.member.neutron.member_get_ip(None, m, True)
        name = self.a.member._get_name(m, ip)

        self.set_count_2()
        self.a.member.delete(None, m)

        pool_name = self.a.member._pool_name(None, m['pool_id'])
        self.a.last_client.slb.service_group.member.delete.assert_called_with(
            pool_name, name, m['protocol_port'])
