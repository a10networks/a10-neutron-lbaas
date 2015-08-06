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

from neutron.db import l3_db
try:
    from neutron.db import db_base_plugin_v2
    from neutron.db.portbindings_db import PortBindingPort as PortBindingPort
    from neutron_lbaas.db.loadbalancer import models as lb_db
except ImportError:
    # v2 does not exist before Kilo
    pass


class NeutronOpsV2(object):

    def __init__(self, handler):
        self.openstack_driver = handler.openstack_driver
        self.plugin = self.openstack_driver.plugin
        self.ndbplugin = db_base_plugin_v2.NeutronDbPluginV2()

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

    def _get_portbindingport(self, context, port_id):
        with context.session.begin():
            port_binding = (context.session.query(PortBindingPort)
                            .filter_by(port_id=port_id).first())
            return port_binding

    def _create_or_update_portbindingport(self, context, port_id, host):
        port_binding = None
        with context.session.begin():
            port_binding = self._get_portbindingport(context, port_id)
            if port_binding:
                port_binding.host = host
                port_binding.update()
            else:
                port_binding = self._create_portbindingport(port_id, host)
        return port_binding

    def _create_portbindingport(self, context, port_id, host):
        port_binding = PortBindingPort()
        port_binding.port_id = port_id
        port_binding.host = host
        with context.session.begin(subtransactions=True):
            context.session.add(port_binding)
        return port_binding

    def _get_port(self, context, port_id):
        return self.ndbplugin.get_port(context, port_id)

    def _delete_portbinding(self, context, port_id):
        with context.session.begin(subtransactions=True):
            binding = self._get_portbindingport(context, port_id)
            if binding:
                context.session.delete(binding)

    def portbindingport_create_or_update(self, context, pool_id, host):
        return self._create_or_update_portbindingport(context, pool_id, host)

    def portbindingport_create_or_update_from_vip_id(self, context, vip_id, host):
        vip = self.neutron_ops.vip_get(context, vip_id)
        port_id = vip.port_id
        return self._create_or_update_portbindingport(context, port_id, host)

    def portbindingport_delete(self, context, port_id):
        return self._delete_portbinding(port_id)
