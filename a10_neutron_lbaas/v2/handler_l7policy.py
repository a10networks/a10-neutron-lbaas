# Copyright 2019, Omkar Telee (omkartelee01), A10 Networks
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

import logging

import acos_client.errors as acos_errors

from a10_neutron_lbaas.v2 import handler_base_v2
from a10_neutron_lbaas.v2 import v2_context as a10

from a10_neutron_lbaas.v2.policy import PolicyUtil

LOG = logging.getLogger(__name__)


class L7PolicyHandler(handler_base_v2.HandlerBaseV2):
    def _set(self, set_method, c, context, file="", script="", size=0, action="", **kwargs):
        set_method(file=file, script=script, size=size, action=action)

    def create(self, context, l7policy, **kwargs):
        with a10.A10WriteStatusContext(self, context, l7policy) as c:
            try:
                filename = l7policy.id
                action = "import"
                p = PolicyUtil()
                script = p.createPolicy(l7policy)
                size = len(script.encode('utf-8'))
                self._set(c.client.slb.aflex_policy.create,
                          c, context, filename, script, size, action)
                old_listener = l7policy.listener
                new_listener = l7policy.listener
                get_listener = c.client.slb.virtual_server.vport.get(old_listener.loadbalancer_id,
                                                                     old_listener.name,
                                                                     old_listener.protocol,
                                                                     old_listener.protocol_port)

                if 'aflex-scripts' in get_listener['port']:
                    aflex_scripts = get_listener['port']['aflex-scripts']
                    aflex_scripts.append({"aflex": filename})
                    new_listener.aflex = aflex_scripts
                else:
                    new_listener.aflex = [{"aflex": filename}]
                self.a10_driver.listener.update(context, old_listener, new_listener)
            except acos_errors.Exists:
                pass

    def update(self, context, old_l7policy, l7policy, **kwargs):
        self.create(context, l7policy, **kwargs)

    def _delete(self, c, context, l7policy):
        LOG.debug("L7PolicyHandler.delete(): l7policy=%s, context=%s" % (l7policy.id, context))
        try:
            old_listener = l7policy.listener
            new_listener = l7policy.listener
            get_listener = c.client.slb.virtual_server.vport.get(old_listener.loadbalancer_id,
                                                                 old_listener.name,
                                                                 old_listener.protocol,
                                                                 old_listener.protocol_port)
            # removing listener attachment
            if 'aflex-scripts' in get_listener['port']:
                aflex_scripts = get_listener['port']['aflex-scripts']
                new_aflex_scripts = []
                for aflex in aflex_scripts:
                    if aflex['aflex'] != l7policy.id:
                        new_aflex_scripts.append(aflex)
                new_listener.aflex = new_aflex_scripts
            self.a10_driver.listener.update(context, old_listener, new_listener)
            c.client.slb.aflex_policy.delete(l7policy.id)
        except acos_errors.Exists:
                pass

    def delete(self, context, l7policy):
        with a10.A10DeleteContext(self, context, l7policy) as c:
            self._delete(c, context, l7policy)
