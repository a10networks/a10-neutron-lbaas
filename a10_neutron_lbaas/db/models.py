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


from a10_neutron_lbaas.db import api as db_api

Base = db_api.get_base()


def _uuid_str():
    return str(uuid.uuid4())


def _get_date():
    return datetime.datetime.now()


class A10Base(Base):
    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=uuid_str)
    tenant_id = sa.Column(sa.String(36), nullable=False)
    created_at = sa.Column(sa.DateTime, default=_get_date)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date)


class A10TenantBinding(A10Base):
    __tablename__ = "a10_tenant_bindings"

    device_name = sa.Column(sa.String(1024), nullable=False)


class A10DeviceInstance(A10Base):
    """An orchestrated vThunder that is being used as a device."""

    __tablename__ = 'a10_device_instances'

    # This field is directly analagous to the device name in config.py;
    # and will be used as such throughout.
    name = sa.Column(sa.String(1024), nullable=False)

    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    # TODO(dougwig) -- these should come from static config
    # api_version = sa.Column(sa.String(12), nullable=False)
    # api_protocol = sa.Column(sa.String(255), nullable=False)
    # api_port = sa.Column(sa.Integer, nullable=False)
    nova_instance_id = sa.Column(sa.String(36), nullable=True)
    ip_address = sa.Column(sa.String(255), nullable=False)

    def to_dict(self):
        # TODO(dougwig) - return device dict entry
        raise Foobar()


class A10SLB(A10Base):
    __tablename__ = 'a10_slbs'

    device_name = sa.Column(sa.String(1024), nullable=False)

    # LBaaS v1 or v2, only one of these will be defined
    vip_id = sa.Column(sa.String(36))
    lbaas_loadbalancer_id = sa.Column(sa.String(36))

    def get_lbaas_root(self):
        # TODO(dougwig), if vip, lookup and return vip, if lb, same
        raise Foobar()
