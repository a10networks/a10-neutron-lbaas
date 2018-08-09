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
import sqlalchemy.orm as orm
import uuid

from a10_neutron_lbaas.db import model_base


def _uuid_str():
    return str(uuid.uuid4())


class A10Device(model_base.A10BaseMixin, model_base.A10Base):

    __tablename__ = 'a10_devices'

    # This field is directly analagous to the device name in config.py;
    # and will be used as such throughout.
    name = sa.Column(sa.String(1024), nullable=False)
    description = sa.Column(sa.String(255), nullable=True)

    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)

    api_version = sa.Column(sa.String(12), nullable=False)
    protocol = sa.Column(sa.String(32), nullable=False)
    port = sa.Column(sa.Integer, nullable=False)

    nova_instance_id = sa.Column(sa.String(36), nullable=True)
    host = sa.Column(sa.String(255), nullable=False)

    a10_opts = orm.relationship("A10DeviceValue", back_populates="associated_device")


class A10DeviceKey(model_base.A10Base):

    __tablename__ = 'a10_device_key'

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=_uuid_str)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
    description = sa.Column(sa.String(1024), nullable=False)
    associated_value = orm.relationship("A10DeviceValue", back_populates="associated_key")


class A10DeviceValue(model_base.A10Base, model_base.A10BaseMixin):

    __tablename__ = 'a10_device_value'

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=_uuid_str)
    associated_obj_id = sa.Column(sa.String(36), sa.ForeignKey('a10_devices.id'), nullable=False)
    key_id = sa.Column(sa.String(36), sa.ForeignKey('a10_device_key.id'), nullable=False)

    value = sa.Column(sa.String(255), nullable=True)

    associated_device = orm.relationship("A10Device", back_populates="a10_opts")
    associated_key = orm.relationship("A10DeviceKey", back_populates="associated_value")
