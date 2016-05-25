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


class A10TenantBinding(model_base.A10BaseMixin, model_base.A10Base):
    __tablename__ = "a10_tenant_bindings"

    device_name = sa.Column(sa.String(1024), nullable=False)

    # XXX(dougwig) -- remove this in favor of find_by()
    @classmethod
    def find_by_tenant_id(cls, tenant_id, db_session=None):
        return cls.find_by_attribute('tenant_id', tenant_id, db_session)
