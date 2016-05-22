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

from a10_neutron_lbaas.vthunder import keystone as a10_keystone

import vthunder_user_tenant


class VThunderPerTenantPlumbingHooks(vthunder_user_tenant.VThunderPerTenantPlumbingHooks):

    def _get_ks_sessions(self, a10_context, cfg, vth):
        ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'),
            vthunder_config=vth)
        network_ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'),
            openstack_context=a10_context.openstack_context)
        return (ks, network_ks)


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active, for one vthunder per VIP.
# LBaaS v2 ONLY.

class VThunderPerVIPPlumbingHooks(vthunder_user_tenant.VThunderPerVIPPlumbingHooks):

    def _get_ks_sessions(self, a10_context, cfg, vth):
        ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'),
            vthunder_config=vth)
        network_ks = a10_keystone.KeystoneA10(
            cfg.get('keystone_version'), cfg.get('keystone_auth_url'),
            openstack_context=a10_context.openstack_context)
        return (ks, network_ks)
