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
from neutron_lbaas.db.loadbalancerv2 import LoadBalancerPluginDbv2 as lb_db
from neutron_lbaas.db.loadbalancer import models

def status_update(context):

    for lb in lb_db.get_loadbalancers(context):
        with a10.A10Context(self, context, lb) as c:
            try:
                name = self.meta(lb, 'id', lb.id)
                oper_stats = c.client.slb.virtual_server.oper(name)
            
                lb_db.update_status(context, model.LoadBalancer, lb.id, operating_status=oper_stats)
            except Exception:
                pass
        if lb.get("pool"):
            pool = lb.get("pool")
            with a10.A10Context(self, context, pool) as c:
                name = pool.id
                if name is not None:
                    oper_stats = c.client.slb.service_group.oper(name)
                    lb_db.update_status(context, model.Pool, pool.id, operating_status=oper_stats)
            for member in pool.get("members"):
                try:
                    with a10.A10Context(self, context, member) as c:
                        server_ip = self.neutron.member_get_ip(context, member,
                                                               c.device_cfg['use_float'])
                        server_name = self._meta_name(member, server_ip)
                        oper_stats = c.client.slb.service_group.member.oper(name=server_name)
                        lb_db.update_status(context, model.Member, member.id, operating_status=oper_stats)
                 except Exception as e:
                    pass
