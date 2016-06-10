#   Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from a10_neutron_lbaas.v2 import handler_lb
from a10_neutron_lbaas.v2 import handler_member
from a10_neutron_lbaas.v2 import handler_pool

import logging

from a10_neutron_lbaas.v1 import handler_member

logging.basicConfig()
LOG = logging.getLogger(__name__)


def status_update_v2(a10_driver):
    lb_db = a10_driver.plugin.db
    context = ncontext.get_admin_context()
    for lb in lb_db.get_loadbalancers(context):
        for pool in lb.pools:
            for member in pool.members:
                member_h = handler_member.MemberHandler(a10_driver,
                                                        a10_driver.openstack_driver.member,
                                                        neutron=a10_driver.neutron)
                member_h.oper(context, member, lb_db, models.MemberV2, pool)

def status_update_v1(a10_driver):
    lb_db = a10_driver.plugin.db
    context = ncontext.get_admin_context()
    for vip in lb_db.get_vips(context):
        for pool in vip.pools:
            for member in pool.members:
                member_h = handler_member.MemberHandler(a10_driver,
                                                        a10_driver.openstack_driver.member,
                                                        neutron=a10_driver.neutron)
                member_h.oper(context, member, lb_db, models.Member, pool)
