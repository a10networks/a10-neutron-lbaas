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


class L7RuleHandler(handler_base_v2.HandlerBaseV2):

    def _set(self, set_method, c, context, file="", script="", size=0, action="", **kwargs):
        set_method(file=file, script=script, size=size, action=action)

    def create(self, context, l7rule, **kwargs):
        l7policy = l7rule.policy
        with a10.A10WriteStatusContext(self, context, l7policy) as c:
            try:
                filename = l7policy.id
                action = "import"
                p = PolicyUtil()
                script = p.createPolicy(l7policy)
                size = len(script.encode('utf-8'))
                self._set(c.client.slb.aflex_policy.create,
                          c, context, filename, script, size, action)
            except acos_errors.Exists:
                pass

    def update(self, context, old_l7rule, l7rule, **kwargs):
        self.create(context, l7rule, **kwargs)

    def delete(self, context, l7rule):
        with a10.A10DeleteContext(self, context, l7rule):
            policy = l7rule.policy
            rules = l7rule.policy.rules
            for index, rule in enumerate(rules):
                if rule.id == l7rule.id:
                    del rules[index]
                    break
            policy.rules = rules
            l7rule.policy = policy
            self.create(context, l7rule)
