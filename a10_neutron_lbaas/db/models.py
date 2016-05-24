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

from contextlib import contextmanager
import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.inspection import inspect

from a10_neutron_lbaas.db import api as db_api

Base = db_api.get_base()


def _uuid_str():
    return str(uuid.uuid4())


def _get_date():
    return datetime.datetime.now()


class A10Base(Base):
    __abstract__ = True

    @classmethod
    @contextmanager
    def _query(cls, db_session=None):
        with db_api.magic_session(db_session) as db:
            yield db.query(cls)

    @classmethod
    def get(cls, key, db_session=None):
        with cls._query(db_session) as q:
            return q.get(key)

    @classmethod
    def find_all_by(cls, db_session=None, **kwargs):
        with cls._query(db_session) as q:
            return q.filter_by(**kwargs).all()

    @classmethod
    def find_by(cls, db_session=None, **kwargs):
        with cls._query(db_session) as q:
            return q.filter_by(**kwargs).one_or_none()

    @classmethod
    def find_by_attribute(cls, attribute_name, attribute, db_session=None):
        with cls._query(db_session) as q:
            return q.filter(
                getattr(cls, attribute_name) == attribute).one_or_none()

    @classmethod
    def find_all(cls, db_session=None):
        with cls._query(db_session) as q:
            return q.all()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        # Populate all the unspecified columns with their defaults
        for key, column in inspect(cls).columns.items():
            if key not in kwargs and column.default is not None:
                arg = column.default.arg
                column_default = arg if callable(arg) else lambda: arg
                setattr(instance, key, column_default(instance))
        return instance

    @classmethod
    def create_and_save(cls, db_session=None, **kwargs):
        m = cls.create(**kwargs)
        with db_api.magic_session(db_session) as db:
            db.add(m)
            db.commit()
            return m

    def as_dict(self):
        d = dict(self.__dict__)
        d.pop('_sa_instance_state', None)
        return d

    def update(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def delete(self, db_session=None):
        db = db_session or inspect(self).session
        db.delete(self)

    created_at = sa.Column(sa.DateTime, default=_get_date, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date, nullable=False)


class A10BaseMixin(object):

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=_uuid_str)
    tenant_id = sa.Column(sa.String(36), nullable=False)


class A10TenantBinding(A10BaseMixin, A10Base):
    __tablename__ = "a10_tenant_bindings"

    device_name = sa.Column(sa.String(1024), nullable=False)

    # TODO(dougwig) -- later - I bet a decorator could replace this boilerplate
    @classmethod
    def find_by_tenant_id(cls, tenant_id, db_session=None):
        return cls.find_by_attribute('tenant_id', tenant_id, db_session)


class A10DeviceInstance(A10BaseMixin, A10Base):
    """An orchestrated vThunder that is being used as a device."""

    __tablename__ = 'a10_device_instances'

    # This field is directly analagous to the device name in config.py;
    # and will be used as such throughout.
    name = sa.Column(sa.String(1024), nullable=False)

    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)

    api_version = sa.Column(sa.String(12), nullable=False)
    protocol = sa.Column(sa.String(32), nullable=False)
    port = sa.Column(sa.Integer, nullable=False)
    autosnat = sa.Column(sa.Boolean(), nullable=False)
    v_method = sa.Column(sa.String(32), nullable=False)
    shared_partition = sa.Column(sa.String(1024), nullable=False)
    use_float = sa.Column(sa.Boolean(), nullable=False)
    default_virtual_server_vrid = sa.Column(sa.Integer, nullable=True)
    ipinip = sa.Column(sa.Boolean(), nullable=False)
    write_memory = sa.Column(sa.Boolean(), nullable=False)

    nova_instance_id = sa.Column(sa.String(36), nullable=True)
    ip_address = sa.Column(sa.String(255), nullable=False)

    # TODO(dougwig) -- later - reference to scheduler, or capacity, or?
    # TODO(dougwig) -- later - should add state enum here

    # For "device" dicts, use a10_config.get_device()
    # For client objects, use _get_a10_client with the a10_config device dict


class A10SLB(A10BaseMixin, A10Base):
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
