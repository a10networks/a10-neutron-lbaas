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

import sqlalchemy as sa

from a10_neutron_lbaas.db import model_base


class A10SLB(model_base.A10BaseMixin, model_base.A10Base):
    __tablename__ = 'a10_slbs'

    # For vip specific binding (as opposed to tenant level binding), this will
    # differ from A10TenantBinding, if that row exists at all.
    device_name = sa.Column(sa.String(1024), nullable=False)

    # LBaaS v1 or v2, only one of these will be defined
    pool_id = sa.Column(sa.String(36))

    loadbalancer_id = sa.Column(sa.String(36))

    @classmethod
    def find_by_loadbalancer_id(cls, loadbalancer_id, db_session=None):
        return cls.find_by_attribute('loadbalancer_id', loadbalancer_id, db_session)
#     # TODO(dougwig) -- later - should add state enum here

#     # def get_lbaas_root(self):
#     #     # TODO(dougwig), later - if vip, lookup and return vip, if lb, same
#     #     raise Foobar()
