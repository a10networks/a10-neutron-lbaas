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

from neutron.db import db_base_plugin_v2
from neutron.db.portbindings_db import PortBindingPort as PortBindingPort


class NeutronDBV1(object):

    # This class exposes the portbindingports table in the DB as neutron_ops
    # doesn't provide direct access.

    def __init__(self, ndbplugin=None, neutron_ops=None):
        self.ndbplugin = ndbplugin or db_base_plugin_v2.NeutronDbPluginV2()
        self.neutron_ops = neutron_ops

    # This stuff should be moved into a DB class.
    # Neutron does not expose creation of port/host bindings so it's gotta go somewhere
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

    def _delete_portbinding(self, context, port_id):
        with context.session.begin(subtransactions=True):
            binding = self._get_portbindingport(context, port_id)
            if binding:
                context.session.delete(binding)

    def _create_portbindingport(self, context, port_id, host):
        port_binding = PortBindingPort()
        port_binding.port_id = port_id
        port_binding.host = host
        with context.session.begin(subtransactions=True):
            context.session.add(port_binding)
        return port_binding

    def _get_port(self, context, port_id):
        return self.ndbplugin.get_port(context, port_id)

    def portbindingport_create_or_update(self, context, pool_id, host):
        return self._create_or_update_portbindingport(context, pool_id, host)

    def portbindingport_create_or_update_from_vip_id(self, context, vip_id, host):
        vip = self.neutron_ops.vip_get(context, vip_id)
        port_id = vip.port_id
        return self._create_or_update_portbindingport(context, port_id, host)

    def portbindingport_delete(self, context, port_id):
        return self._delete_portbinding(context, port_id)
