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

import acos_client.errors as acos_errors
import handler_base
import v1_context as a10


class MemberHandler(handler_base.HandlerBase):

    def _model_type(self):
        return 'member'

    def _get_ip(self, context, member, use_float=False):
        return self.openstack_driver._member_get_ip(context, member, use_float)

    def _get_name(self, member, ip_address):
        tenant_label = member['tenant_id'][:5]
        addr_label = str(ip_address).replace(".", "_", 4)
        server_name = "_%s_%s_neutron" % (tenant_label, addr_label)
        return server_name

    def _count(self, context, member):
        return self.openstack_driver._member_count(context, member)

    def _create(self, c, context, member):
        server_ip = self._get_ip(context, member,
                                 c.device_cfg['use_float'])
        server_name = self._get_name(member, server_ip)

        status = c.client.slb.UP
        if not member['admin_state_up']:
            status = c.client.slb.DOWN

        try:
            c.client.slb.server.create(server_name, server_ip)
        except (acos_errors.Exists, acos_errors.AddressSpecifiedIsInUse):
            pass

        try:
            c.client.slb.service_group.member.create(
                member['pool_id'],
                server_name,
                member['protocol_port'],
                status=status)
        except acos_errors.Exists:
            pass

    def create(self, context, member):
        with a10.A10WriteStatusContext(self, context, member) as c:
            self._create(c, context, member)

    def update(self, context, old_member, member):
        with a10.A10WriteStatusContext(self, context, member) as c:
            server_ip = self._get_ip(context, member,
                                     c.device_cfg['use_float'])
            server_name = self._get_name(member, server_ip)

            status = c.client.slb.UP
            if not member['admin_state_up']:
                status = c.client.slb.DOWN

            try:
                c.client.slb.service_group.member.update(
                    member['pool_id'],
                    server_name,
                    member['protocol_port'],
                    status)
            except acos_errors.NotFound:
                # Adding db relation after the fact
                self._create(c, context, member)

    def _delete(self, c, context, member):
        server_ip = self._get_ip(context, member, c.device_cfg['use_float'])
        server_name = self._get_name(member, server_ip)

        if self._count(context, member) > 1:
            c.client.slb.service_group.member.delete(member['pool_id'],
                                                     server_name,
                                                     member['protocol_port'])
        else:
            c.client.slb.server.delete(server_name)

    def delete(self, context, member):
        with a10.A10DeleteContext(self, context, member) as c:
            self._delete(c, context, member)
