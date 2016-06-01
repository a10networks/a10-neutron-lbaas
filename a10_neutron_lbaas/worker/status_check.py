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
from a10_neutron_lbaas.v2 import handler_member

from neutron import context as ncontext
from neutron_lbaas.db.loadbalancer.loadbalancer_dbv2 import LoadBalancerPluginDbv2
from neutron_lbaas.db.loadbalancer import models


import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)


def status_update(a10_driver):
    lb_db = LoadBalancerPluginDbv2()
    context = ncontext.get_admin_context()
    for lb in lb_db.get_loadbalancers(context):
        for pool in lb.pools:
            for member in pool.members:
                member_h = handler_member.MemberHandler(a10_driver,
                                                        a10_driver.openstack_driver.member,
                                                        neutron=a10_driver.neutron)
                member_h.oper(context, member, lb_db, models.MemberV2, pool)
