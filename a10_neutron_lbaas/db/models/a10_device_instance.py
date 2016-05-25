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

from a10_neutron_lbaas.db import model_base


class A10DeviceInstance(model_base.A10BaseMixin, model_base.A10Base):
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
    host = sa.Column(sa.String(255), nullable=False)

    # TODO(dougwig) -- later - reference to scheduler, or capacity, or?
    # TODO(dougwig) -- later - should add state enum here

    # For "device" dicts, use a10_config.get_device()
    # For client objects, use _get_a10_client with the a10_config device dict
