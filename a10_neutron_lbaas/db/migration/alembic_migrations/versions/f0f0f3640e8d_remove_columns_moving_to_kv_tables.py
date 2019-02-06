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

"""Remove columns moving to kv tables

Revision ID: f0f0f3640e8d
Revises: 937e131388f2
Create Date: 2018-08-28 04:49:14.985299

"""

# revision identifiers, used by Alembic.
revision = 'f0f0f3640e8d'
down_revision = '937e131388f2'
branch_labels = None
depends_on = None

from alembic import op  # noqa
from datetime import datetime
import sqlalchemy as sa  # noqa
import sqlalchemy.sql as sasql  # noqa
import uuid


def upgrade():
    op.drop_column('a10_devices', 'autosnat')
    op.drop_column('a10_devices', 'default_virtual_server_vrid')
    op.drop_column('a10_devices', 'ipinip')
    op.drop_column('a10_devices', 'shared_partition')
    op.drop_column('a10_devices', 'use_float')
    op.drop_column('a10_devices', 'v_method')
    op.drop_column('a10_devices', 'write_memory')
    op.alter_column('a10_devices', 'name',
                    existing_type=sa.String(1024), nullable=True)
    op.alter_column('a10_device_value', 'value',
                    existing_type=sa.String(255), nullable=True)
    op.alter_column('a10_device_key', 'description',
                    existing_type=sa.String(1024), nullable=True)
    op.add_column('a10_device_key',
                  sa.Column('default_value', sa.String(255), nullable=True))
    op.add_column('a10_device_key',
                  sa.Column('data_type', sa.String(255), nullable=True))

    key_table = sasql.table(
        'a10_device_key',
        sasql.column('id', sa.String),
        sasql.column('name', sa.String),
        sasql.column('created_at', sa.DateTime),
        sasql.column('updated_at', sa.DateTime),
        sasql.column('description', sa.String),
        sasql.column('data_type', sa.String),
        sasql.column('default_value', sa.String))
    dt = str(datetime.now())
    keys = [
        {'name': 'arp_disable', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': 'Disable ARP replies from a virtual server.',
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'autosnat', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': 'Source address translation is configured on the VIP.',
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'conn_limit', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Specify the maximum number of concurrent connections '
                         'allowed on a real server.'),
         'default_value': '8000000', 'data_type': 'integer'},
        {'name': 'conn_resume', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Specify the maximum number of connections the '
                         'server can have before the ACOS device resumes use '
                         'of the server. Use does not resume until the '
                         'nummber of connections reaches the configured '
                         'maximum or less.'),
         'default_value': '0', 'data_type': 'integer'},
        {'name': 'default_virtual_server_vrid', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Virtual servers will be created on this VRID. The '
                         'VRID must already be configured on the device.'),
         'default_value': '', 'data_type': 'string'},
        {'name': 'ha_conn_mirror', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Enable connection mirroring (session '
                         'synchronization) for the virtual port.'),
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'ha_sync_list', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Contains a list of hostnames or IP addresses that '
                         'the driver will run the `ha sync` command against '
                         'whenever a write operation occurs.'),
         'default_value': '[]', 'data_type': 'literal'},
        {'name': 'ipinip', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Enables IP-in-IP tunneling. This option is available '
                         'only on the following port types: TCP, UDP, RSTP, '
                         'FTP, MMS, SIP, TFTP and Radius.'),
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'member_expressions', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('JSON structure of config options which are applied '
                         'if the member server\'s name matches the regex.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'no_dest_nat', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': 'Disable destination NAT.',
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'plumb_vlan_dhcp', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': 'Configure the VE Interface to use DHCP',
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'service_group_expressions', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('JSON structure of config options which are applied '
                         'if the service group\'s name matches the regex.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'shared_partition', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('If using a shared partition (v_method=LSI), then '
                         'this field configures which partition to use. By '
                         'default, it is the main shared partition.'),
         'default_value': 'shared', 'data_type': 'string'},
        {'name': 'source_nat_pool', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Set to the name of a nat pool to use that pool for '
                         'source nat on vports the nat pool must already exist '
                         'on the ACOS device.'),
         'default_value': '', 'data_type': 'string'},
        {'name': 'template_virtual_server', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Apply the defined virtual server template to all '
                         'newly defined virtual servers.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'use_float', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Utilize the floating address of the member and not '
                         'the actual interface ip.'),
         'default_value': '0', 'data_type': 'boolean'},
        {'name': 'v_method', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Partition method; "LSI" to put all slb\'s in a '
                         'single shared partition, or "ADP" to use a partition '
                         'per tenant. Partitions are RBA style in ACOS 2.x, '
                         'and L3V in ACOS 4.x.'),
         'default_value': 'LSI', 'data_type': 'string'},
        {'name': 'virtual_server_expressions', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('JSON structure of config options which are applied '
                         'if the virtual server\'s name matches the regex.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'vlan_binding_level', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Hierarchical Port Binding Level that the VLAN will '
                         'exist in.'),
         'default_value': '0', 'data_type': 'integer'},
        {'name': 'vlan_interfaces', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': 'Interfaces the VLAN will be bound to.',
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'vport_defaults', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('JSON structure of config options which are applied '
                         'as default values to all vports.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'vport_expressions', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('JSON structure of config options which are applied '
                         'if the vport\'s name matches the regex.'),
         'default_value': '{}', 'data_type': 'literal'},
        {'name': 'write_memory', 'id': str(uuid.uuid4()),
         'created_at': op.inline_literal(dt),
         'updated_at': op.inline_literal(dt),
         'description': ('Enable or disable calling write memory directly '
                         'after any operation that changes ACOS\'s running '
                         'state. Turning this off also disables all ha sync '
                         'operations, regardless of the settings in '
                         'ha-sync-list.'),
         'default_value': '1', 'data_type': 'boolean'}]
    op.bulk_insert(key_table, keys, multiinsert=False)


def downgrade():
    op.add_column('a10_devices',
                  sa.Column('autosnat', sa.Boolean(), nullable=False))
    op.add_column('a10_devices',
                  sa.Column('default_virtual_server_vrid', sa.Integer,
                            nullable=True))
    op.add_column('a10_devices',
                  sa.Column('ipinip', sa.Boolean(), nullable=False))
    op.add_column('a10_devices',
                  sa.Column('shared_partition', sa.String(1024),
                            nullable=False))
    op.add_column('a10_devices',
                  sa.Column('use_float', sa.Boolean(), nullable=False))
    op.add_column('a10_devices',
                  sa.Column('v_method', sa.String(32), nullable=False))
    op.add_column('a10_devices',
                  sa.Column('write_memory', sa.Boolean(), nullable=False))
    op.alter_column('a10_device_value', 'value',
                    existing_type=sa.String(255), nullable=False)
    op.alter_column('a10_device_key', 'description',
                    existing_type=sa.String(1024), nullable=False)
    op.alter_column('a10_devices', 'name',
                    existing_type=sa.String(1024), nullable=False)
    op.drop_column('a10_device_key', 'default_value')
    op.drop_column('a10_device_key', 'data_type')
    op.execute('DELETE FROM a10_device_key;')
