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

import sqlalchemy as sa
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import inspect
from sqlalchemy.orm import backref, relationship

from a10_neutron_lbaas.db import model_base as models


LOG = logging.getLogger(__name__)


class A10ScalingGroup(models.A10Base):
    """A10 Scaling Group - container of switch and workers"""

    __tablename__ = u'a10_scaling_groups'

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    tenant_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    scaling_policy_id = sa.Column(sa.String(36),
                                  sa.ForeignKey('a10_scaling_policies.id'),
                                  nullable=True)

    scaling_policy = relationship('A10ScalingPolicy', backref='scaling_groups')
    switches = relationship('A10ScalingGroupSwitch')
    workers = relationship('A10ScalingGroupWorker')
    members = relationship('A10ScalingGroupMember', backref='scaling_group')

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }


class A10ScalingGroupBinding(models.A10Base):
    __tablename__ = u'a10_scaling_group_bindings'

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   nullable=False,
                   default=models._uuid_str)
    scaling_group_id = sa.Column(sa.String(36),
                                 sa.ForeignKey('a10_scaling_groups.id'),
                                 nullable=False)
    scaling_group = relationship(A10ScalingGroup, backref='bindings')

    lbaas_loadbalancer_id = sa.Column(sa.String(36),
                                      unique=True,
                                      nullable=False)


class A10ScalingGroupMember(models.A10Base):
    """A10 Scaling Group Member - switch/worker depending on 'role'"""
    __tablename__ = "a10_scaling_group_members"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    type = sa.Column(sa.String(50), nullable=False)
    scaling_group_id = sa.Column(sa.String(36),
                                 sa.ForeignKey('a10_scaling_groups.id'),
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
    nova_instance_id = sa.Column(sa.String(36), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type
    }

    def add_virtual_server(self, neutron_id, **kwargs):
        vs = A10ScalingGroupMemberVirtualServer.create(
            neutron_id=neutron_id,
            **kwargs)
        self.virtual_servers.append(vs)
        return vs

    def get_virtual_server(self, neutron_id):
        return inspect(self).session.\
            query(A10ScalingGroupMemberVirtualServer).\
            filter_by(member_id=self.id, neutron_id=neutron_id).\
            first()

    def delete_virtual_server(self, neutron_id):
        vs = self.get_virtual_server(neutron_id)
        if vs:
            inspect(self).session.delete(vs)


class A10ScalingGroupWorker(A10ScalingGroupMember):
    __tablename__ = "a10_scaling_group_workers"

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_scaling_group_members.id'),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }


class A10ScalingGroupSwitch(A10ScalingGroupMember):
    __tablename__ = "a10_scaling_group_switches"

    id = sa.Column(sa.String(36),
                   sa.ForeignKey(u'a10_scaling_group_members.id'),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }


class A10ScalingGroupMemberVirtualServer(models.A10Base):
    __tablename__ = "a10_scaling_group_member_virtual_servers"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    member_id = sa.Column(sa.String(36),
                          sa.ForeignKey(u'a10_scaling_group_members.id'),
                          nullable=False)
    member = relationship('A10ScalingGroupMember',
                          backref=backref('virtual_servers', cascade='all, delete-orphan'))
    neutron_id = sa.Column(sa.String(36),
                           nullable=False)

    ip_address = sa.Column(sa.String(50), nullable=False)
    interface_ip_address = sa.Column(sa.String(50), nullable=True)
    sflow_uuid = sa.Column(sa.String(36), nullable=False)

    def add_port(self, port, **kwargs):
        vs = A10ScalingGroupMemberVirtualServerPort.create(
            port=port,
            **kwargs)
        self.ports.append(vs)
        return vs

    def get_port(self, port):
        return inspect(self).session.\
            query(A10ScalingGroupMemberVirtualServerPort).\
            filter_by(virtual_server_id=self.id, port=port).\
            first()

    def delete_port(self, port):
        port = self.get_port(port)
        if port:
            inspect(self).session.delete(port)


class A10ScalingGroupMemberVirtualServerPort(models.A10Base):
    __tablename__ = "a10_scaling_group_member_virtual_server_ports"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    virtual_server_id = sa.Column(sa.String(36),
                                  sa.ForeignKey(u'a10_scaling_group_member_virtual_servers.id'),
                                  nullable=False)
    virtual_server = relationship('A10ScalingGroupMemberVirtualServer',
                                  backref=backref('ports', cascade='all, delete-orphan'))
    port = sa.Column(sa.Integer,
                     nullable=False)
    protocol = sa.Column(sa.String(255), nullable=False)
    sflow_uuid = sa.Column(sa.String(36), nullable=False)


class A10ScalingPolicy(models.A10Base):
    __tablename__ = "a10_scaling_policies"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    tenant_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)

    cooldown = sa.Column(sa.Integer, nullable=False)
    min_instances = sa.Column(sa.Integer, nullable=False)
    max_instances = sa.Column(sa.Integer, nullable=True)

    reactions = relationship('A10ScalingPolicyReaction',
                             order_by="A10ScalingPolicyReaction.position",
                             collection_class=ordering_list('position'),
                             backref='policy')

    def scaling_group_ids(self):
        return [sg.id for sg in self.scaling_groups]


class A10ScalingPolicyReaction(models.A10Base):
    __tablename__ = "a10_scaling_policy_reactions"

    # A surrogate key is required by ordering_list
    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    scaling_policy_id = sa.Column(sa.String(36),
                                  sa.ForeignKey('a10_scaling_policies.id'),
                                  nullable=False)
    position = sa.Column(sa.Integer,
                         nullable=False)
    alarm_id = sa.Column(sa.String(36),
                         sa.ForeignKey('a10_scaling_alarms.id'),
                         nullable=False)
    action_id = sa.Column(sa.String(36),
                          sa.ForeignKey('a10_scaling_actions.id'),
                          nullable=False)

    alarm = relationship('A10ScalingAlarm', backref='reactions')
    action = relationship('A10ScalingAction', backref='reactions')


class A10ScalingAlarm(models.A10Base):
    __tablename__ = "a10_scaling_alarms"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    tenant_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)

    aggregation = sa.Column(sa.String(50), nullable=False)
    measurement = sa.Column(sa.String(50), nullable=False)
    operator = sa.Column(sa.String(50), nullable=False)
    threshold = sa.Column(sa.Float(), nullable=False)
    unit = sa.Column(sa.String(50), nullable=False)
    period = sa.Column(sa.Integer, nullable=False)
    period_unit = sa.Column(sa.String(50), nullable=False)

    def scaling_group_ids(self):
        return set(x
                   for reaction in self.reactions
                   for x in reaction.policy.scaling_group_ids())


class A10ScalingAction(models.A10Base):
    __tablename__ = "a10_scaling_actions"

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=models._uuid_str,
                   nullable=False)
    tenant_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)

    action = sa.Column(sa.String(50), nullable=False)
    amount = sa.Column(sa.Integer)

    def scaling_group_ids(self):
        return set(x
                   for reaction in self.reactions
                   for x in reaction.policy.scaling_group_ids())
