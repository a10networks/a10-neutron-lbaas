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

try:
    from neutron.db import l3_db
except ImportError:
    pass
try:
    from neutron_lbaas.db.loadbalancer import models as lb_db
except ImportError:
    # v2 does not exist before Kilo
    pass


class NeutronOpsV2(object):

    def __init__(self, handler):
        self.openstack_driver = handler.openstack_driver
        self.plugin = self.openstack_driver.plugin

    def member_get_ip(self, context, member, use_float=False):
        ip_address = member.address
        if use_float:
            fip_qry = context.session.query(l3_db.FloatingIP)
            if (fip_qry.filter_by(fixed_ip_address=ip_address).count() > 0):
                float_address = fip_qry.filter_by(
                    fixed_ip_address=ip_address).first()
                ip_address = str(float_address.floating_ip_address)
        return ip_address

    def member_count(self, context, member):
        return context.session.query(lb_db.MemberV2).filter_by(
            tenant_id=member.tenant_id,
            address=member.address).count()

    def loadbalancer_total(self, context, tenant_id):
        return context.session.query(lb_db.LoadBalancer).filter_by(
            tenant_id=tenant_id).count()

    def pool_get(self, context, pool_id):
        return self.plugin.db.get_pool(context, pool_id)

    def bcm_factory(self):
        from neutron_lbaas.services.loadbalancer.plugin import CERT_MANAGER_PLUGIN
        return CERT_MANAGER_PLUGIN.CertManager()

    def vip_get(self, context, vip_id):
        return self.plugin.db.get_vip(context, vip_id)
