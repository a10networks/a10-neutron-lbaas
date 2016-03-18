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
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()


class A10TenantBinding(Base):
    __tablename__ = "a10_tenant_bindings"

    id = sa.Column(sa.Integer, primary_key=True)
    tenant_id = sa.Column(sa.String(36), nullable=False)
    device_name = sa.Column(sa.String(1024), nullable=False)
