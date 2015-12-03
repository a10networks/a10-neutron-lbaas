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


# class A10ApplianceSLB(model_base.BASEV2):
#     __tablename__ = u'a10_appliances_slb'

#     id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
#     type = sa.Column(sa.String(50), nullable=False)

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__,
#         'polymorphic_on': type
#     }


# class A10ApplianceConfigured(A10ApplianceSLB):
#     """An a10 appliance defined in the config.py configuration file"""

#     __tablename__ = u'a10_appliances_configured'

#     id = sa.Column(sa.String(36),
#                    sa.ForeignKey(u'a10_appliances_slb.id'),
#                    primary_key=True,
#                    default=uuid_str,
#                    nullable=False)
#     device_key = sa.Column(sa.String(255), nullable=False)

#     def device(self, context):
#         return context.a10_driver.config.devices[self.device_key]

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__
#     }


# class A10ApplianceDB(A10ApplianceSLB):
#     """An a10 appliance defined in the database"""

#     __tablename__ = u'a10_appliances_db'

#    def device(self, context):
#        config_device = context.a10_driver.config.devices[self.device_key]
#        device = config_device.copy()
#        device['appliance'] = self
#        return device


#     id = sa.Column(sa.String(36),
#                    sa.ForeignKey(u'a10_appliances_slb.id'),
#                    primary_key=True,
#                    default=uuid_str,
#                    nullable=False)
#     tenant_id = sa.Column(sa.String(255), nullable=True)
#     name = sa.Column(sa.String(255), nullable=True)
#     description = sa.Column(sa.String(255), nullable=True)
#     host = sa.Column(sa.String(255), nullable=False)
#     api_version = sa.Column(sa.String(12), nullable=False)
#     username = sa.Column(sa.String(255), nullable=False)
#     password = sa.Column(sa.String(255), nullable=False)

#     def device(self, context):
#         return context.a10_driver.config.devices[self.device_key]

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__
#     }


# class A10SLB(model_base.BASEV2):
#     __tablename__ = u'a10_slb'

#     id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
#     type = sa.Column(sa.String(50), nullable=False)
#     a10_appliance_id = sa.Column(sa.String(36),
#                                  sa.ForeignKey('a10_appliances_slb.id'),
#                                  nullable=False)
#     a10_appliance = relationship(A10ApplianceSLB)

#    def device(self, context):
#        return {
#            'appliance': self,
#            'host': self.host,
#            'api_version': self.api_version,
#            'username': self.username,
#            'password': self.password
#        }

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__,
#         'polymorphic_on': type
#     }


# class A10SLBV1(A10SLB):
#     __tablename__ = u'a10_slb_v1'

#     id = sa.Column(sa.String(36),
#                    sa.ForeignKey(u'a10_slb.id'),
#                    primary_key=True,
#                    default=uuid_str,
#                    nullable=False)
#     vip_id = sa.Column(sa.String(36),
#                        sa.ForeignKey(u'vips.id'),
#                        unique=True,
#                        nullable=False)

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__
#     }


# class A10SLBV2(A10SLB):
#     __tablename__ = u'a10_slb_v2'

#     id = sa.Column(sa.String(36),
#                    sa.ForeignKey(u'a10_slb.id'),
#                    primary_key=True,
#                    default=uuid_str,
#                    nullable=False)
#     lbaas_loadbalancer_id = sa.Column(sa.String(36),
#                                       sa.ForeignKey(u'lbaas_loadbalancers.id'),
#                                       unique=True,
#                                       nullable=False)

#     __mapper_args__ = {
#         'polymorphic_identity': __tablename__
#     }



class A10TenantBinding(Base):
    __tablename__ = "a10_tenant_bindings"

    id = sa.Column(sa.String(36), default=_uuid_str, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=_get_date)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date)
    tenant_id = sa.Column(sa.String(36), nullable=False)
    device_name = sa.Column(sa.String(1024), nullable=False)
