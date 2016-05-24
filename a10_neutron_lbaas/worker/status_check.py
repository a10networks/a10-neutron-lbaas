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

# todo -- file this in
import logging

from neutron_lbaas.db.loadbalancer.loadbalancer_dbv2 import LoadBalancerPluginDbv2
from neutron_lbaas.db.loadbalancer import models
from neutron import context as ncontext

from a10_neutron_lbaas.v2 import v2_context
from a10_neutron_lbaas.v2 import handler_hm
from a10_neutron_lbaas.v2 import handler_lb
from a10_neutron_lbaas.v2 import handler_listener
from a10_neutron_lbaas.v2 import handler_member
from a10_neutron_lbaas.v2 import handler_pool

logging.basicConfig()
LOG = logging.getLogger(__name__)

def status_update(a10_driver):
    lb_db = LoadBalancerPluginDbv2()
    LOG.info("TRACER")
    context = ncontext.get_admin_context()
    for lb in lb_db.get_loadbalancers(context):    
        #lb_h = handler_lb.LoadbalancerHandler( a10_driver, a10_driver.openstack_driver.load_balancer, neutron=a10_driver.neutron)
        #lb_h.oper(context, lb, lb_db, models.LoadBalancer)
        LOG.info("TRACER_LB")
        for pool in lb.pools:
            #pool_h = handler_pool.PoolHandler( a10_driver, a10_driver.openstack_driver.pool, neutron=a10_driver.neutron)
            #pool_h.oper(context, pool, lb_db, models.PoolV2)
            LOG.info("TRACER_POOL")
            for member in pool.members:
                member_h = handler_member.MemberHandler( a10_driver, a10_driver.openstack_driver.member, neutron=a10_driver.neutron)
                member_h.oper(context, member, lb_db, models.MemberV2, pool)
                LOG.info("TRACER_MEMBER")