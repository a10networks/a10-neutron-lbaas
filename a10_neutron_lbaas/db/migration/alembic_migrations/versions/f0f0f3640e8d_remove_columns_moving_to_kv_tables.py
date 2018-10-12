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
    op.alter_column('a10_device_value', 'value', existing_type=sa.String(255), nullable=True)
    op.alter_column('a10_device_key', 'description', existing_type=sa.String(1024), nullable=True)
    op.add_column('a10_device_key',
                  sa.Column('default_value', sa.String(255), nullable=True))
    op.add_column('a10_device_key',
                  sa.Column('data_type', sa.String(255), nullable=True))

    key_table = sasql.table('a10_device_key',
        sasql.column('id', sa.String),
        sasql.column('name', sa.String),
        sasql.column('description', sa.String),
        sasql.column('data_type', sa.String),
        sasql.column('default_value', sa.String))
    keys = [
        {'id': str(uuid.uuid4()), 'name': 'shared_partition',
         'description':'',
         'default_value': 'shared', 'data_type': 'string'},
        {'id': str(uuid.uuid4()), 'name': 'v_method',
         'description':'',
         'default_value': 'LSI', 'data_type': 'string'},
        {'id': str(uuid.uuid4()), 'name': 'write_memory',
         'description':'',
         'default_value': '1', 'data_type': 'boolean'},
        {'id': str(uuid.uuid4()), 'name': 'source_nat_pool',
         'description':'',
         'default_value': '', 'data_type': 'string'},
        {'id': str(uuid.uuid4()), 'name': 'autosnat',
         'description':'',
         'default_value': '0', 'data_type': 'boolean'},
        {'id': str(uuid.uuid4()), 'name': 'ipinip',
         'description':'',
         'default_value': '0', 'data_type': 'boolean'},
        {'id': str(uuid.uuid4()), 'name': 'use_float',
         'description':'',
         'default_value': '0', 'data_type': 'boolean'},
        {'id': str(uuid.uuid4()), 'name': 'default_virtual_server_vrid',
         'description':'',
         'default_value': '', 'data_type': 'string'},
        {'id': str(uuid.uuid4()), 'name': 'conn_limit',
         'description':'',
         'default_value': '8000000', 'data_type': 'string'}]
    op.bulk_insert(key_table, keys)

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
    op.alter_column('a10_device_value', 'value', existing_type=sa.String(255), nullable=False)
    op.alter_column('a10_device_key', 'description', existing_type=sa.String(1024), nullable=False)
    op.drop_column('a10_device_key', 'default_value')
    op.drop_column('a10_device_key', 'data_type')
    op.execute('DELETE FROM a10_device_key;')
