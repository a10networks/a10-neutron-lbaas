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
import a10_neutron_lbaas.acos_client_extensions
import a10_neutron_lbaas.acos_client_extensions as acos_client_extensions
import a10_neutron_lbaas.nova_plumbing_client as nova_plumbing_client


from a10_neutron_lbaas.db import api as db_api

Base = db_api.get_base()


def _uuid_str():
    return str(uuid.uuid4())


def _get_date():
    return datetime.datetime.now()


class HelperBase(Base):

    @classmethod
    def find_by_attribute(cls, attribute_name, attribute, db_session=None):
        db = db_session or db_api.get_session()
        return db.query(cls).filter(
                getattr(cls, attribute_name) == attribute).one_or_none()

    @classmethod
    def find_all(cls, db_session=None):
        db = db_session or db_api.get_session()
        return db.query(cls).all()

    @classmethod
    def create_and_save(cls, db_session=None, **kwargs):
        db = db_session or db_api.get_session()
        m = cls(**kwargs)
        db.add(m)
        db.commit()


class A10Base(Base):
    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
    tenant_id = sa.Column(sa.String(36), nullable=False)
    created_at = sa.Column(sa.DateTime, default=_get_date)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date)


class A10TenantBinding(A10Base):
    __tablename__ = "a10_tenant_bindings"

    device_name = sa.Column(sa.String(1024), nullable=False)

    # TODO(dougwig) -- later - I bet a decorator could replace this boilerplate
    @classmethod
    def find_by_tenant_id(cls, tenant_id, db_session=None):
        return self.find_by_attribute('tenant_id', tenant_id, db_session)


class A10DeviceInstance(A10Base):
    """An orchestrated vThunder that is being used as a device."""

    __tablename__ = 'a10_device_instances'

    # This field is directly analagous to the device name in config.py;
    # and will be used as such throughout.
    name = sa.Column(sa.String(1024), nullable=False)

    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)

    api_version = sa.Column(sa.String(12), nullable=False)
    api_protocol = sa.Column(sa.String(255), nullable=False)
    api_port = sa.Column(sa.Integer, nullable=False)

    protocol = sa.Column(sa.String(32), nullable=False)
    port = sa.Column(sa.Integer, nullable=False)
    autosnat = sa.Column(sa.Boolean(), nullable=False)
    v_method = sa.Column(sa.String(32), nullable=False)
    shared_partition = sa.Column(sa.String(1024), nullable=False)
    use_float = sa.Column(sa.Boolean(), nullable=False)
    default_virtual_server_vrid = sa.Column(sa.Integer, nullable=False)
    ipinip = sa.Column(sa.Boolean(), nullable=False)
    write_memory = sa.Column(sa.Boolean(), nullable=False)

    nova_instance_id = sa.Column(sa.String(36), nullable=True)
    ip_address = sa.Column(sa.String(255), nullable=False)

    # TODO(dougwig) -- later - reference to scheduler, or capacity, or?
    # TODO(dougwig) -- later - should add state enum here

    # For "device" dicts, use a10_config.get_device()
    # For client objects, use _get_a10_client with the a10_config device dict


class A10SLB(A10Base):
    __tablename__ = 'a10_slbs'

    # For vip specific binding (as opposed to tenant level binding), this will
    # differ from A10TenantBinding, if that row exists at all.
    device_name = sa.Column(sa.String(1024), nullable=False)

    # LBaaS v1 or v2, only one of these will be defined
    vip_id = sa.Column(sa.String(36))
    loadbalancer_id = sa.Column(sa.String(36))

    # TODO(dougwig) -- later - should add state enum here

    def get_lbaas_root(self):
        # TODO(dougwig), if vip, lookup and return vip, if lb, same
        raise Foobar()
