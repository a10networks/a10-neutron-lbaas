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

import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm

from a10_neutron_lbaas.db import model_base
from a10_neutron_lbaas.db.models.a10_device_instance import A10DeviceInstance

def _uuid_str():
    return str(uuid.uuid4())


class A10DeviceConfigKey(model_base.A10Base):

    __tablename__ = 'a10_device_config_key'

    id = sa.Column(sa.String(32), primary_key=True, default=_uuid_str, nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1024), nullable=False)



class A10DeviceConfigValue(model_base.A10Base):

    __tablename__ = 'a10_device_config_value'

    id = sa.Column(sa.String(32), primary_key=True, default=_uuid_str, nullable=False)
    device_id = sa.Column(sa.String(36), sa.ForeignKey('a10_device_instances.id'), nullable=False)
    config_key_id = sa.Column(sa.String(32), sa.ForeignKey('a10_device_config_key.id'), nullable=False)

    value = sa.Column(sa.String(255), nullable=False)

    uuid = orm.relationship(A10DeviceInstance, uselist=False)
    config_key = orm.relationship(A10DeviceConfigKey, uselist=False)
