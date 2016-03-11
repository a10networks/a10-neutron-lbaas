# Copyright 2015,  A10 Networks
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
#    under the License.from neutron.db import model_base

from neutron.db import model_base
import sqlalchemy as sa
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship
import uuid

import a10_neutron_lbaas.acos_client_extensions as acos_client_extensions


def default(cls, **kw):
    instance = cls(**kw)
    populate(instance)
    return instance


def populate(instance):
    for key, column in inspect(instance.__class__).columns.items():
        if getattr(instance, key) is None and column.default is not None:
            arg = column.default.arg
            column_default = arg if callable(arg) else lambda: arg
            setattr(instance, key, column_default(instance))


def summon(session, cls, **kw):
    existing = session.query(cls).filter_by(**kw).first()
    if existing is None:
        existing = default(cls, **kw)
        session.add(existing)
    return existing


def delete_all(session, query):
    """Sql-alchemy's Query.delete() doesn't remove rows from polymorphically related tables"""

    for row in query:
        session.delete(row)


def uuid_str():
    return str(uuid.uuid4())


class A10ApplianceSLB(model_base.BASEV2):
    __tablename__ = u'a10_appliances_slb'

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
    type = sa.Column(sa.String(50), nullable=False)

    def device(self, context):
        raise NotImplementedError()

    def client(self, context):
        device_cfg = self.device(context)
        return context.a10_driver._get_a10_client(device_cfg)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type
    }


class A10ApplianceConfigured(A10ApplianceSLB):
    """An a10 appliance defined in the config.py configuration file"""

    __tablename__ = u'a10_appliances_configured'

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_appliances_slb.id'),
                   primary_key=True,
                   default=uuid_str,
                   nullable=False)
    device_key = sa.Column(sa.String(255), nullable=False)

    def device(self, context):
        config_device = context.a10_driver.config.devices[self.device_key]
        device = config_device.copy()
        device['appliance'] = self
        return device

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }


class A10ApplianceDB(A10ApplianceSLB):
    """An a10 appliance defined in the database"""

    __tablename__ = u'a10_appliances_db'

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_appliances_slb.id'),
                   primary_key=True,
                   default=uuid_str,
                   nullable=False)
    tenant_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    host = sa.Column(sa.String(255), nullable=False)
    api_version = sa.Column(sa.String(12), nullable=False)
    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    protocol = sa.Column(sa.String(255), nullable=False)
    port = sa.Column(sa.Integer, nullable=False)
    nova_instance_id = sa.Column(sa.String(36), nullable=True)

    def device(self, context):
        # TODO(aritrary config): When we store all the options
        # we shouldn't neet to get defaults from the config
        config = context.a10_driver.config
        device = {
            'appliance': self,
            'host': self.host,
            'api_version': self.api_version,
            'username': self.username,
            'password': self.password,
            'protocol': self.protocol,
            'port': self.port
        }
        return config.device_defaults(device)

    def client(self, context):
        if self.nova_instance_id is not None:
            device_cfg = self.device(context)
            acos_client = context.a10_driver.acos_client_class(device_cfg)
            patient_client = acos_client_extensions.patient_client(acos_client)
            client = context.a10_driver.client_class(patient_client, device_cfg)
            return client

        return super(A10ApplianceDB, self).client(context)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }


class A10SLB(model_base.BASEV2):
    __tablename__ = u'a10_slb'

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
    type = sa.Column(sa.String(50), nullable=False)
    a10_appliance_id = sa.Column(sa.String(36),
                                 sa.ForeignKey('a10_appliances_slb.id'),
                                 nullable=False)
    a10_appliance = relationship(A10ApplianceSLB, backref='slbs')

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type
    }


class A10SLBV1(A10SLB):
    __tablename__ = u'a10_slb_v1'

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_slb.id'),
                   primary_key=True,
                   default=uuid_str,
                   nullable=False)
    vip_id = sa.Column(sa.String(36),
                       sa.ForeignKey(u'vips.id'),
                       unique=True,
                       nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }


class A10SLBV2(A10SLB):
    __tablename__ = u'a10_slb_v2'

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_slb.id'),
                   primary_key=True,
                   default=uuid_str,
                   nullable=False)
    lbaas_loadbalancer_id = sa.Column(sa.String(36),
                                      sa.ForeignKey(u'lbaas_loadbalancers.id'),
                                      unique=True,
                                      nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }


class A10TenantAppliance(model_base.BASEV2):
    __tablename__ = u'a10_tenant_appliance'

    tenant_id = sa.Column(sa.String(255),
                          primary_key=True,
                          nullable=False)
    a10_appliance_id = sa.Column(sa.String(36),
                                 sa.ForeignKey('a10_appliances_slb.id'),
                                 nullable=False)
    a10_appliance = relationship(A10ApplianceSLB)
