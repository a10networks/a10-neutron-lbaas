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

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models

import vthunder_per_tenant

LOG = logging.getLogger(__name__)


# This next set of plumbing hooks needs to be used when the vthunder
# scheduler is active, for one vthunder per VIP.
# LBaaS v2 ONLY.

class VThunderPerVIPPlumbingHooks(vthunder_per_tenant.VThunderPerTenantPlumbingHooks):

    def select_device_with_lbaas_obj(self, tenant_id, a10_context, lbaas_obj,
                                     db_session=None, **kwargs):

        if not self.driver.config.get('use_database'):
            raise ex.RequiresDatabase('vThunder orchestration requires use_database=True')

        # If we already have a vThunder, use it.
        # one vthunder per VIP

        missing_instance = (
            'A10 instance mapped to tenant %s is not present in db; '
            'add it back to config or migrate loadbalancers' % tenant_id
        )

        root_id = lbaas_obj.root_loadbalancer.id
        slb = models.A10SLB.find_by(loadbalancer_id=root_id, db_session=db_session)
        if slb is not None:
            d = self.driver.config.get_device(slb.device_name, db_session=db_session)
            if d is None:
                LOG.error(missing_instance)
                raise ex.InstanceMissing(missing_instance)

            LOG.debug("select_device, returning cached instance %s", d)
            return d

        # No? Then we need to create one.

        if kwargs.get('action') != 'create':
            LOG.error(missing_instance)
            raise ex.InstanceMissing(missing_instance)

        device_config = self._create_instance(tenant_id, a10_context, lbaas_obj, db_session)
        self._wait_for_instance(device_config)

        # Now make sure that we remember where it is.

        models.A10SLB.create_and_save(
            tenant_id=tenant_id,
            device_name=device_config['name'],
            loadbalancer_id=root_id,
            db_session=db_session)

        LOG.debug("select_device, returning new instance %s", device_config)
        return device_config
