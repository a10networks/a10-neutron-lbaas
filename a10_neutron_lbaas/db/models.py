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

import datetime
import uuid

import sqlalchemy as sa

from a10_neutron_lbaas.db import api as db_api

Base = db_api.get_base()


def _uuid_str():
    return str(uuid.uuid4())


def _get_date():
    return datetime.datetime.now()


class A10TenantBinding(Base):
    __tablename__ = "a10_tenant_bindings"

    id = sa.Column(sa.String(36), default=_uuid_str, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=_get_date)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date)
    tenant_id = sa.Column(sa.String(36), nullable=False)
    device_name = sa.Column(sa.String(1024), nullable=False)
